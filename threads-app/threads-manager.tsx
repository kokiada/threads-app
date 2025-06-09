"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Bell,
  User,
  Home,
  Calendar,
  Users,
  BarChart3,
  Settings,
  Plus,
  Check,
  AlertCircle,
  Upload,
  Clock,
  Menu,
  X,
} from "lucide-react"

// Sample data
const accounts = [
  { id: 1, name: "アカウント1", status: "active", avatar: "/placeholder.svg?height=40&width=40" },
  { id: 2, name: "アカウント2", status: "active", avatar: "/placeholder.svg?height=40&width=40" },
  { id: 3, name: "アカウント3", status: "expired", avatar: "/placeholder.svg?height=40&width=40" },
]

const scheduledPosts = [
  { date: "2025/3/7 10:00", account: "アカウント1" },
  { date: "2025/3/8 15:30", account: "アカウント2" },
  { date: "2025/3/9 08:45", account: "アカウント3" },
]

const recentPosts = [
  { date: "2025/3/6 09:00", status: "success" },
  { date: "2025/3/5 17:30", status: "success" },
  { date: "2025/3/4 12:15", status: "failed" },
]

const navigationItems = [
  { id: "home", icon: Home, label: "ホーム" },
  { id: "schedule", icon: Calendar, label: "スケジュール" },
  { id: "accounts", icon: Users, label: "アカウント" },
  { id: "analytics", icon: BarChart3, label: "分析" },
  { id: "settings", icon: Settings, label: "設定" },
]

export default function ThreadsManager() {
  const [activeTab, setActiveTab] = useState("home")
  const [isNewPostModalOpen, setIsNewPostModalOpen] = useState(false)
  const [isAddAccountModalOpen, setIsAddAccountModalOpen] = useState(false)
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [postContent, setPostContent] = useState("")
  const [selectedAccounts, setSelectedAccounts] = useState<number[]>([])
  const [postTiming, setPostTiming] = useState("now")
  const [scheduledDate, setScheduledDate] = useState("")
  const [scheduledTime, setScheduledTime] = useState("")

  const handleAccountToggle = (accountId: number) => {
    setSelectedAccounts((prev) =>
      prev.includes(accountId) ? prev.filter((id) => id !== accountId) : [...prev, accountId],
    )
  }

  const resetNewPostForm = () => {
    setPostContent("")
    setSelectedAccounts([])
    setPostTiming("now")
    setScheduledDate("")
    setScheduledTime("")
  }

  const handleNewPostSubmit = () => {
    console.log("New post submitted:", {
      content: postContent,
      accounts: selectedAccounts,
      timing: postTiming,
      scheduledDate,
      scheduledTime,
    })
    setIsNewPostModalOpen(false)
    resetNewPostForm()
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="p-6 border-b">
        <h2 className="text-xl font-bold text-indigo-600">Threads投稿マネージャー</h2>
      </div>
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {navigationItems.map((item) => (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className={`w-full justify-start gap-3 h-12 ${
                activeTab === item.id
                  ? "bg-indigo-600 text-white hover:bg-indigo-700"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
              onClick={() => {
                setActiveTab(item.id)
                setIsMobileSidebarOpen(false)
              }}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Button>
          ))}
        </div>
      </nav>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="md:hidden fixed top-0 left-0 right-0 z-50 bg-indigo-600 text-white h-15 flex items-center justify-between px-4 shadow-lg">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-indigo-700"
            onClick={() => setIsMobileSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-semibold">Threads投稿マネージャー</h1>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="text-white hover:bg-indigo-700">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-white hover:bg-indigo-700">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </header>

      {/* Desktop Header */}
      <header className="hidden md:block fixed top-0 left-64 right-0 z-40 bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            {navigationItems.find((item) => item.id === activeTab)?.label}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="text-gray-600 hover:bg-gray-100">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-gray-600 hover:bg-gray-100">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </header>

      {/* Mobile Sidebar Overlay */}
      {isMobileSidebarOpen && (
        <div
          className="md:hidden fixed inset-0 z-50 bg-black bg-opacity-50"
          onClick={() => setIsMobileSidebarOpen(false)}
        >
          <div className="fixed left-0 top-0 bottom-0 w-64 bg-white shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">メニュー</h2>
              <Button variant="ghost" size="icon" onClick={() => setIsMobileSidebarOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <SidebarContent />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="hidden md:block fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 shadow-sm z-30">
        <SidebarContent />
      </aside>

      {/* Main Content */}
      <main className="pt-15 pb-20 px-4 md:pt-16 md:pb-8 md:pl-64 md:pr-0">
        <div className="max-w-none md:max-w-7xl md:mx-auto md:px-6">
          {/* Dashboard */}
          {activeTab === "home" && (
            <div className="space-y-6 mt-4">
              {/* Desktop: 3-column grid, Mobile: single column */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Account Overview Card */}
                <Card className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <CardTitle className="text-lg">アカウント概要</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold text-indigo-600">3</div>
                        <div className="text-sm text-gray-600">登録アカウント数</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">2</div>
                        <div className="text-sm text-gray-600">有効なアカウント</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-blue-600">12</div>
                        <div className="text-sm text-gray-600">今週の投稿数</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Scheduled Posts Card */}
                <Card className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <CardTitle className="text-lg">予定投稿</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {scheduledPosts.map((post, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <Clock className="h-4 w-4 text-gray-500" />
                          <div className="flex-1">
                            <div className="text-sm font-medium">{post.date}</div>
                            <div className="text-xs text-gray-600">{post.account}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Posts Card */}
                <Card className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <CardTitle className="text-lg">最近の投稿</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {recentPosts.map((post, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <div className="text-sm">{post.date}</div>
                          <Badge
                            variant={post.status === "success" ? "default" : "destructive"}
                            className={post.status === "success" ? "bg-green-500" : ""}
                          >
                            {post.status === "success" ? (
                              <>
                                成功 <Check className="h-3 w-3 ml-1" />
                              </>
                            ) : (
                              <>
                                失敗 <AlertCircle className="h-3 w-3 ml-1" />
                              </>
                            )}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Additional dashboard content for larger screens */}
              <div className="hidden lg:block">
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <Card className="hover:shadow-lg transition-shadow duration-200">
                    <CardHeader>
                      <CardTitle className="text-lg">週間パフォーマンス</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-32 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg flex items-center justify-center">
                        <p className="text-gray-600">チャート表示エリア</p>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="hover:shadow-lg transition-shadow duration-200">
                    <CardHeader>
                      <CardTitle className="text-lg">クイックアクション</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-3">
                        <Button variant="outline" className="h-12">
                          <Calendar className="h-4 w-4 mr-2" />
                          スケジュール確認
                        </Button>
                        <Button variant="outline" className="h-12">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          レポート生成
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* Account Management */}
          {activeTab === "accounts" && (
            <div className="space-y-6 mt-4">
              <div className="max-w-4xl">
                <Card className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <CardTitle className="text-lg">アカウント管理</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {accounts.map((account) => (
                        <div
                          key={account.id}
                          className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <Avatar className="h-12 w-12">
                            <AvatarImage src={account.avatar || "/placeholder.svg"} />
                            <AvatarFallback>{account.name[0]}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="font-medium text-lg">{account.name}</div>
                            <Badge
                              variant={account.status === "active" ? "default" : "destructive"}
                              className={account.status === "active" ? "bg-green-500 mt-1" : "mt-1"}
                            >
                              {account.status === "active" ? (
                                <>
                                  接続済み <Check className="h-3 w-3 ml-1" />
                                </>
                              ) : (
                                <>
                                  トークン更新が必要 <AlertCircle className="h-3 w-3 ml-1" />
                                </>
                              )}
                            </Badge>
                          </div>
                          <div className="hidden md:flex gap-2">
                            <Button variant="outline" size="sm">
                              編集
                            </Button>
                            <Button variant="outline" size="sm">
                              設定
                            </Button>
                          </div>
                        </div>
                      ))}
                      <Dialog open={isAddAccountModalOpen} onOpenChange={setIsAddAccountModalOpen}>
                        <DialogTrigger asChild>
                          <Button className="w-full md:w-auto" variant="outline">
                            <Plus className="h-4 w-4 mr-2" />
                            新しいアカウントを追加
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-md">
                          <DialogHeader>
                            <DialogTitle>アカウント追加</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label htmlFor="account-name">アカウント名</Label>
                              <Input id="account-name" placeholder="アカウント名を入力" />
                            </div>
                            <div className="p-4 bg-blue-50 rounded-lg">
                              <p className="text-sm text-blue-800">
                                認証を開始すると、Threadsアカウントとの連携が始まります。
                                指示に従って認証を完了してください。
                              </p>
                            </div>
                            <Button className="w-full bg-indigo-600 hover:bg-indigo-700">認証を開始</Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* Other tabs content */}
          {activeTab === "schedule" && (
            <div className="mt-4 text-center py-12">
              <Calendar className="h-16 w-16 mx-auto text-gray-400 mb-4" />
              <h2 className="text-xl font-semibold text-gray-700 mb-2">スケジュール機能</h2>
              <p className="text-gray-600">カレンダービューとスケジュール管理機能は開発中です</p>
            </div>
          )}

          {activeTab === "analytics" && (
            <div className="mt-4 text-center py-12">
              <BarChart3 className="h-16 w-16 mx-auto text-gray-400 mb-4" />
              <h2 className="text-xl font-semibold text-gray-700 mb-2">分析ダッシュボード</h2>
              <p className="text-gray-600">詳細な分析とレポート機能は開発中です</p>
            </div>
          )}

          {activeTab === "settings" && (
            <div className="mt-4 text-center py-12">
              <Settings className="h-16 w-16 mx-auto text-gray-400 mb-4" />
              <h2 className="text-xl font-semibold text-gray-700 mb-2">設定</h2>
              <p className="text-gray-600">アプリケーション設定は開発中です</p>
            </div>
          )}
        </div>
      </main>

      {/* FAB */}
      <Dialog open={isNewPostModalOpen} onOpenChange={setIsNewPostModalOpen}>
        <DialogTrigger asChild>
          <Button
            className="fixed bottom-20 right-4 md:bottom-8 md:right-8 h-14 w-14 rounded-full bg-pink-500 hover:bg-pink-600 shadow-lg z-40 transition-all duration-200 hover:scale-110"
            size="icon"
          >
            <Plus className="h-6 w-6" />
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>新規投稿</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Account Selection */}
            <div>
              <Label className="text-sm font-medium">投稿するアカウント</Label>
              <div className="space-y-2 mt-2">
                {accounts
                  .filter((account) => account.status === "active")
                  .map((account) => (
                    <div key={account.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`account-${account.id}`}
                        checked={selectedAccounts.includes(account.id)}
                        onCheckedChange={() => handleAccountToggle(account.id)}
                      />
                      <Label htmlFor={`account-${account.id}`} className="flex items-center gap-2">
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={account.avatar || "/placeholder.svg"} />
                          <AvatarFallback>{account.name[0]}</AvatarFallback>
                        </Avatar>
                        {account.name}
                      </Label>
                    </div>
                  ))}
              </div>
            </div>

            {/* Post Content */}
            <div>
              <Label htmlFor="post-content">投稿内容</Label>
              <Textarea
                id="post-content"
                placeholder="投稿内容を入力してください..."
                value={postContent}
                onChange={(e) => setPostContent(e.target.value)}
                className="min-h-[120px] resize-none"
              />
              <div className="text-right text-sm text-gray-500 mt-1">{postContent.length}/500</div>
            </div>

            {/* Media Upload */}
            <div>
              <Label>メディア</Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors cursor-pointer">
                <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">画像や動画をアップロード</p>
                <p className="text-xs text-gray-500 mt-1">またはファイルをドラッグ&ドロップ</p>
              </div>
            </div>

            {/* Timing Options */}
            <div>
              <Label>投稿タイミング</Label>
              <RadioGroup value={postTiming} onValueChange={setPostTiming} className="mt-2">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="now" id="now" />
                  <Label htmlFor="now">今すぐ投稿</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="scheduled" id="scheduled" />
                  <Label htmlFor="scheduled">スケジュール投稿</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Schedule Date/Time */}
            {postTiming === "scheduled" && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="schedule-date">日付</Label>
                  <Input
                    id="schedule-date"
                    type="date"
                    value={scheduledDate}
                    onChange={(e) => setScheduledDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="schedule-time">時刻</Label>
                  <Input
                    id="schedule-time"
                    type="time"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button variant="outline" className="flex-1" onClick={() => setIsNewPostModalOpen(false)}>
                キャンセル
              </Button>
              <Button
                className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                onClick={handleNewPostSubmit}
                disabled={!postContent.trim() || selectedAccounts.length === 0}
              >
                {postTiming === "now" ? "投稿する" : "スケジュール"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 z-50">
        <div className="max-w-md mx-auto">
          <div className="flex justify-around">
            {navigationItems.map((tab) => (
              <Button
                key={tab.id}
                variant="ghost"
                size="sm"
                className={`flex flex-col items-center gap-1 h-auto py-2 px-3 ${
                  activeTab === tab.id ? "text-indigo-600" : "text-gray-600"
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                <tab.icon className="h-5 w-5" />
                <span className="text-xs">{tab.label}</span>
              </Button>
            ))}
          </div>
        </div>
      </nav>
    </div>
  )
}
