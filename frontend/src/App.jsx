import React, { useState } from 'react'
import {
  Search,
  Filter,
  Calendar,
  UploadCloud,
  FileText,
  Clock,
  CheckCircle2,
  Building,
  Tag,
  Download,
  AlertCircle
} from 'lucide-react'

const MOCK_NOTICES = [
  {
    id: '1',
    title: 'Registration Deadline and Course Add/Drop for Winter 2026 Semester',
    category: 'Academic',
    department: 'All Departments',
    sender: 'Office of the Registrar',
    publishedDate: '2026-11-20',
    confidenceScore: 0.96,
    deadlines: [
      { title: 'Last Date for Course Add/Drop', dueDate: '2026-12-05' }
    ],
    snippet: 'All undergraduate students are hereby notified that the course registration confirmation and add/drop period will strictly close on December 5, 2026...'
  },
  {
    id: '2',
    title: 'Payment of Tuition & Hall Dues for 4th Year B.Sc. Engineering',
    category: 'Administrative & Financial',
    department: 'CSE',
    sender: 'Comptroller Office',
    publishedDate: '2026-11-18',
    confidenceScore: 0.92,
    deadlines: [
      { title: 'Tuition Fee Payment Without Fine', dueDate: '2026-11-30' }
    ],
    snippet: 'Students of Batch 2022 (4th Year) are advised to clear outstanding semester dues at the Comptroller office or through designated banking channels...'
  },
  {
    id: '3',
    title: 'Inter-Departmental Football Tournament Schedule 2026',
    category: 'Opportunities & Events',
    department: 'All Departments',
    sender: 'Director of Students Welfare (DSW)',
    publishedDate: '2026-11-15',
    confidenceScore: 0.88,
    deadlines: [
      { title: 'Team Roster Submission Deadline', dueDate: '2026-11-25' }
    ],
    snippet: 'Department sports representatives are requested to submit the verified squad list to the Gymnasium office by November 25, 2026...'
  }
]

export default function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedDept, setSelectedDept] = useState('All')
  const [isUploading, setIsUploading] = useState(false)

  const categories = ['All', 'Academic', 'Administrative & Financial', 'Residential & Campus Life', 'Opportunities & Events']
  const departments = ['All', 'CSE', 'EEE', 'CEE', 'MPE', 'BTM']

  const filteredNotices = MOCK_NOTICES.filter(notice => {
    const matchesSearch = notice.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          notice.snippet.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || notice.category === selectedCategory
    const matchesDept = selectedDept === 'All' || notice.department === selectedDept || notice.department === 'All Departments'
    return matchesSearch && matchesCategory && matchesDept
  })

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans">
      {/* Top Navbar */}
      <header className="bg-emerald-800 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-xl tracking-wider text-white border border-emerald-400">
              IR
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">IRIS</h1>
              <p className="text-xs text-emerald-200">IUT Repository & Information System</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsUploading(!isUploading)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-emerald-950 bg-emerald-300 hover:bg-emerald-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-400 cursor-pointer"
            >
              <UploadCloud className="w-4 h-4 mr-2" />
              Upload Notice (CR / Staff)
            </button>
            <div className="text-xs bg-emerald-900/60 px-3 py-1.5 rounded-full border border-emerald-700 text-emerald-200">
              @iut-dhaka.edu
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Search & Notice Stream */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Search Box */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
              <div className="relative">
                <Search className="w-5 h-5 absolute left-3 top-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search notices, exams, fees, holidays (fuzzy search enabled)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-sm"
                />
              </div>

              {/* Filters */}
              <div className="mt-4 flex flex-wrap gap-3 items-center text-xs">
                <div className="flex items-center text-slate-500 font-medium">
                  <Filter className="w-3.5 h-3.5 mr-1" />
                  Category:
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-2.5 py-1 rounded-full border cursor-pointer ${
                        selectedCategory === cat
                          ? 'bg-emerald-800 text-white border-emerald-800'
                          : 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-3 flex flex-wrap gap-2 items-center text-xs">
                <span className="text-slate-500 font-medium">Department:</span>
                {departments.map(dept => (
                  <button
                    key={dept}
                    onClick={() => setSelectedDept(dept)}
                    className={`px-2.5 py-0.5 rounded cursor-pointer ${
                      selectedDept === dept
                        ? 'bg-slate-800 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {dept}
                  </button>
                ))}
              </div>
            </div>

            {/* Ingestion Uploader Preview Box (Conditional) */}
            {isUploading && (
              <div className="bg-emerald-50 border-2 border-dashed border-emerald-300 rounded-xl p-6 text-center space-y-3">
                <UploadCloud className="w-10 h-10 text-emerald-600 mx-auto" />
                <h3 className="font-semibold text-emerald-900">Scan or Upload Official Notice</h3>
                <p className="text-xs text-emerald-700 max-w-md mx-auto">
                  Drag and drop a PDF file or camera photo of a physical notice board circular. OpenCV and Gemini will automatically extract text, sender, and deadlines for your review.
                </p>
                <input type="file" className="text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-700" />
              </div>
            )}

            {/* Notice Cards List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
                <span>Showing {filteredNotices.length} Archived Notices</span>
                <span>Sorted by Most Recent</span>
              </div>

              {filteredNotices.map(notice => (
                <div key={notice.id} className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 hover:border-emerald-400 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <h2 className="font-bold text-slate-900 text-base leading-snug">
                      {notice.title}
                    </h2>
                    <span className="shrink-0 inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      {(notice.confidenceScore * 100).toFixed(0)}% AI Conf.
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-slate-600 line-clamp-2">
                    {notice.snippet}
                  </p>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
                    <div className="flex items-center gap-3">
                      <span className="inline-flex items-center text-slate-700">
                        <Building className="w-3.5 h-3.5 mr-1 text-slate-400" />
                        {notice.sender}
                      </span>
                      <span className="inline-flex items-center text-slate-500">
                        <Tag className="w-3.5 h-3.5 mr-1 text-slate-400" />
                        {notice.category}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-slate-400">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{notice.publishedDate}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Deadlines & Calendar Sidebar */}
          <div className="space-y-6">
            
            {/* Deadlines Widget */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-emerald-700" />
                  <h3 className="font-bold text-slate-900 text-sm">Upcoming Deadlines</h3>
                </div>
                <button
                  title="Export .ics calendar file"
                  className="inline-flex items-center text-xs text-emerald-700 hover:text-emerald-900 font-medium cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5 mr-1" />
                  .ics
                </button>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs">
                  <div className="flex items-center justify-between font-semibold text-amber-900">
                    <span>Tuition Fee Payment</span>
                    <span className="text-amber-700">Nov 30</span>
                  </div>
                  <p className="text-amber-800/80 mt-1">4th Year B.Sc. Engineering fee payment without fine.</p>
                </div>

                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs">
                  <div className="flex items-center justify-between font-semibold text-emerald-900">
                    <span>Course Add/Drop</span>
                    <span className="text-emerald-700">Dec 05</span>
                  </div>
                  <p className="text-emerald-800/80 mt-1">Winter 2026 Semester registration confirmation.</p>
                </div>
              </div>
            </div>

            {/* System Info Banner */}
            <div className="bg-slate-900 text-slate-200 p-5 rounded-xl text-xs space-y-3">
              <div className="flex items-center space-x-2 text-white font-semibold">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>IRIS Permanent Archive</span>
              </div>
              <p className="text-slate-400 leading-relaxed">
                Notices in IRIS are permanently archived with OCR-indexed text, preventing lost notices when removed from notice boards or web pages.
              </p>
              <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500">
                Department of Computer Science & Technology, IUT
              </div>
            </div>

          </div>

        </div>
      </main>
    </div>
  )
}
