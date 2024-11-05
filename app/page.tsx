'use client'

import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import axios from 'axios'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Camera, UserPlus, Clock, FileText, Users, Trash2 } from 'lucide-react'

// Define the DateRange type with required 'from' and 'to'
interface DateRange {
  from: Date
  to: Date
}

export default function AttendanceApp() {
  // State variables
  const [registerImage, setRegisterImage] = useState<File | null>(null)
  const [registerImagePreview, setRegisterImagePreview] = useState<string | null>(null)
  const [attendanceImage, setAttendanceImage] = useState<File | null>(null)
  const [attendanceImagePreview, setAttendanceImagePreview] = useState<string | null>(null)
  const [userId, setUserId] = useState<string>('')

  // Updated state type: DateRange with required 'from' and 'to'
  const [selectedDates, setSelectedDates] = useState<DateRange | undefined>()

  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false)
  const [dialogContent, setDialogContent] = useState<string>('')
  const [isCameraOpen, setIsCameraOpen] = useState<boolean>(false)
  const webcamRef = useRef<Webcam>(null)
  const [cameraType, setCameraType] = useState<'register' | 'attendance'>('register')

  // Updated backendUrl to use environment variable
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000'
  console.log('Backend URL:', backendUrl); // Confirm the backend URL

  const registerInputRef = useRef<HTMLInputElement>(null)
  const attendanceInputRef = useRef<HTMLInputElement>(null)

  // Functions
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>, type: 'register' | 'attendance') => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        if (type === 'register') {
          setRegisterImage(file)
          setRegisterImagePreview(reader.result as string)
        } else {
          setAttendanceImage(file)
          setAttendanceImagePreview(reader.result as string)
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const capturePhoto = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot()
      if (imageSrc) {
        const byteString = atob(imageSrc.split(',')[1])
        const ab = new ArrayBuffer(byteString.length)
        const ia = new Uint8Array(ab)
        for (let i = 0; i < byteString.length; i++) {
          ia[i] = byteString.charCodeAt(i)
        }
        const blob = new Blob([ab], { type: 'image/jpeg' })
        const file = new File([blob], 'captured_photo.jpg', { type: 'image/jpeg' })

        const reader = new FileReader()
        reader.onloadend = () => {
          if (cameraType === 'register') {
            setRegisterImage(file)
            setRegisterImagePreview(reader.result as string)
          } else {
            setAttendanceImage(file)
            setAttendanceImagePreview(reader.result as string)
          }
        }
        reader.readAsDataURL(file)
        // Close camera modal after capturing the photo
        setIsCameraOpen(false)
      }
    }
  }

  const handleRegister = async () => {
    if (!userId || !registerImage) {
      alert('Please enter User ID and select an image.')
      return
    }

    const formData = new FormData()
    formData.append('user_id', userId)
    formData.append('images', registerImage)

    try {
      const response = await axios.post(`${backendUrl}/register`, formData)
      setDialogContent(response.data.message)
      setIsDialogOpen(true)
    } catch (error: any) {
      console.error('Register Error:', error)
      if (error.response) {
        setDialogContent(error.response.data.error || 'An error occurred.')
      } else if (error.request) {
        setDialogContent('No response from server. Please try again later.')
      } else {
        setDialogContent('An unexpected error occurred.')
      }
      setIsDialogOpen(true)
    }
  }

  const handleLogAttendance = async () => {
    if (!attendanceImage) {
      alert('Please select an image.')
      return
    }

    const formData = new FormData()
    formData.append('image', attendanceImage)

    try {
      const response = await axios.post(`${backendUrl}/predict`, formData)
      const predictedUserId = response.data.user_id

      // Log attendance
      await axios.post(`${backendUrl}/attendance`, { user_id: predictedUserId })

      setDialogContent(`Attendance logged for user: ${predictedUserId}`)
      setIsDialogOpen(true)
    } catch (error: any) {
      console.error('Log Attendance Error:', error)
      if (error.response) {
        setDialogContent(error.response.data.message || 'An error occurred.')
      } else if (error.request) {
        setDialogContent('No response from server. Please try again later.')
      } else {
        setDialogContent('An unexpected error occurred.')
      }
      setIsDialogOpen(true)
    }
  }

  const handleGenerateReport = async () => {
    if (!selectedDates?.from || !selectedDates?.to) {
      alert('Please select a date range.')
      return
    }

    const startDate = selectedDates.from.toISOString().split('T')[0]
    const endDate = selectedDates.to.toISOString().split('T')[0]

    try {
      const response = await axios.get(`${backendUrl}/attendance_report`, {
        params: { start_date: startDate, end_date: endDate },
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `attendance_report_${startDate}_to_${endDate}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error: any) {
      console.error('Generate Report Error:', error)
      if (error.response) {
        setDialogContent(error.response.data.error || 'An error occurred.')
      } else if (error.request) {
        setDialogContent('No response from server. Please try again later.')
      } else {
        setDialogContent('An unexpected error occurred.')
      }
      setIsDialogOpen(true)
    }
  }

  const handleListUsers = async () => {
    try {
      const response = await axios.get(`${backendUrl}/list_users`)
      const userIds = response.data.users.map((user: any) => user.user_id)
      setDialogContent('Registered Users:\n' + userIds.join('\n'))
      setIsDialogOpen(true)
    } catch (error: any) {
      console.error('List Users Error:', error)
      if (error.response) {
        setDialogContent(error.response.data.error || 'An error occurred.')
      } else if (error.request) {
        setDialogContent('No response from server. Please try again later.')
      } else {
        setDialogContent('An unexpected error occurred.')
      }
      setIsDialogOpen(true)
    }
  }

  const handleDeleteUser = async () => {
    const deleteUserId = prompt('Enter the User ID to delete:')
    if (!deleteUserId) return

    try {
      await axios.delete(`${backendUrl}/delete_user`, {
        data: { user_id: deleteUserId },
      })
      setDialogContent(`User ${deleteUserId} deleted successfully.`)
      setIsDialogOpen(true)
    } catch (error: any) {
      console.error('Delete User Error:', error)
      if (error.response) {
        setDialogContent(error.response.data.error || 'An error occurred.')
      } else if (error.request) {
        setDialogContent('No response from server. Please try again later.')
      } else {
        setDialogContent('An unexpected error occurred.')
      }
      setIsDialogOpen(true)
    }
  }

  // Custom handler to ensure both 'from' and 'to' are selected
  const handleSelectDates = (range: { from?: Date; to?: Date } | undefined) => {
    if (range?.from && range?.to) {
      setSelectedDates({ from: range.from, to: range.to })
    } else {
      setSelectedDates(undefined)
    }
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl h-[calc(100vh-2rem)] overflow-auto bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-3xl shadow-xl">
        <CardHeader className="sticky top-0 z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg p-4 md:p-6">
          <CardTitle className="text-2xl md:text-3xl font-bold text-center text-gray-800 dark:text-gray-100">
            Facial Recognition Attendance
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 md:p-6 flex flex-col items-center">
          <Tabs defaultValue="register" className="space-y-4 md:space-y-6 w-full">
            <TabsList className="grid grid-cols-3 gap-2 md:gap-4 bg-gray-100 dark:bg-gray-700 p-1 rounded-xl">
              <TabsTrigger value="register" className="rounded-lg data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">Register</TabsTrigger>
              <TabsTrigger value="attendance" className="rounded-lg data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">Attendance</TabsTrigger>
              <TabsTrigger value="reports" className="rounded-lg data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600">Reports</TabsTrigger>
            </TabsList>
            <TabsContent value="register" className="space-y-4 w-full">
              <div className="flex flex-col items-center space-y-4">
                <div className="w-24 h-24 md:w-32 md:h-32 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center overflow-hidden">
                  {registerImagePreview ? (
                    <img src={registerImagePreview} alt="Selected" className="w-full h-full object-cover" />
                  ) : (
                    <Camera className="w-8 h-8 md:w-12 md:h-12 text-gray-400" />
                  )}
                </div>
                {/* Hidden file input */}
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e, 'register')}
                  ref={registerInputRef}
                  className="hidden"
                />
                {/* Buttons */}
                <div className="flex space-x-2">
                  <Button variant="outline" onClick={() => registerInputRef.current?.click()}>
                    Upload Photo
                  </Button>
                  <Button variant="outline" onClick={() => { setCameraType('register'); setIsCameraOpen(true) }}>
                    Take Photo
                  </Button>
                </div>
                <Input
                  placeholder="Enter User ID"
                  className="max-w-xs w-full"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                />
                <Button
                  className="w-full max-w-xs"
                  onClick={handleRegister}
                  disabled={!userId || !registerImage}
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Register User
                </Button>
              </div>
            </TabsContent>
            <TabsContent value="attendance" className="space-y-4 w-full">
              <div className="flex flex-col items-center space-y-4">
                <div className="w-32 h-32 md:w-48 md:h-48 bg-gray-200 dark:bg-gray-700 rounded-2xl flex items-center justify-center overflow-hidden">
                  {attendanceImagePreview ? (
                    <img src={attendanceImagePreview} alt="Selected" className="w-full h-full object-cover" />
                  ) : (
                    <Camera className="w-12 h-12 md:w-16 md:h-16 text-gray-400" />
                  )}
                </div>
                {/* Hidden file input */}
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload(e, 'attendance')}
                  ref={attendanceInputRef}
                  className="hidden"
                />
                {/* Buttons */}
                <div className="flex space-x-2">
                  <Button variant="outline" onClick={() => attendanceInputRef.current?.click()}>
                    Upload Photo
                  </Button>
                  <Button variant="outline" onClick={() => { setCameraType('attendance'); setIsCameraOpen(true) }}>
                    Take Photo
                  </Button>
                </div>
                <Button
                  className="w-full max-w-xs"
                  onClick={handleLogAttendance}
                  disabled={!attendanceImage}
                >
                  <Clock className="w-4 h-4 mr-2" />
                  Log Attendance
                </Button>
              </div>
            </TabsContent>
            <TabsContent value="reports" className="flex flex-col items-center">
              <div className="flex flex-col items-center">
                <Calendar
                  mode="range"
                  selected={selectedDates}
                  onSelect={handleSelectDates}
                  className="rounded-md border"
                />
                <Button
                  className="mt-4"
                  onClick={handleGenerateReport}
                  disabled={!selectedDates}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Report
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex flex-col sm:flex-row justify-between p-4 md:p-6 bg-gray-50 dark:bg-gray-800/50 gap-4">
          <Button variant="outline" className="w-full sm:w-auto" onClick={handleListUsers}>
            <Users className="w-4 h-4 mr-2" />
            List Users
          </Button>
          <Button variant="outline" className="w-full sm:w-auto text-red-500 hover:text-red-700" onClick={handleDeleteUser}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete User
          </Button>
        </CardFooter>
      </Card>

      {/* Dialog for displaying messages */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Notification</DialogTitle>
          </DialogHeader>
          <pre className="whitespace-pre-wrap">{dialogContent}</pre>
          <Button onClick={() => setIsDialogOpen(false)} className="mt-4">
            Close
          </Button>
        </DialogContent>
      </Dialog>

      {/* Dialog for Camera */}
      <Dialog open={isCameraOpen} onOpenChange={setIsCameraOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Take Photo</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{ facingMode: 'user' }}
              className="w-full h-auto rounded-md"
            />
            <Button onClick={capturePhoto} className="mt-4">
              Capture Photo
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

