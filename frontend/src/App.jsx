import { useState } from 'react'
import { FileSearch, Info, X } from 'lucide-react'
import Layout from './components/layout/Layout'
import SearchBar from './components/notices/SearchBar'
import DepartmentFilter from './components/notices/DepartmentFilter'
import NoticeCard from './components/notices/NoticeCard'
import { DEPARTMENTS, MOCK_NOTICES } from './data/mockNotices'

export default function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDepartment, setSelectedDepartment] = useState('All')
  const [selectedNotice, setSelectedNotice] = useState(null)

  const normalizedQuery = searchQuery.trim().toLowerCase()

  const filteredNotices = MOCK_NOTICES.filter((notice) => {
    const matchesDepartment =
      selectedDepartment === 'All' || notice.department === selectedDepartment

    const titleMatch = notice.title.toLowerCase().includes(normalizedQuery)
    const descriptionMatch = (notice.description || '')
      .toLowerCase()
      .includes(normalizedQuery)

    const matchesSearch = !normalizedQuery || titleMatch || descriptionMatch

    return matchesDepartment && matchesSearch
  })

  const handleResetFilters = () => {
    setSearchQuery('')
    setSelectedDepartment('All')
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Page Header */}
        <section className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Notice Archive
          </h1>
          <p className="text-sm text-slate-600">
            Browse and filter official university notices by keyword or department.
          </p>
        </section>

        {/* Search & Department Filter Controls */}
        <section
          aria-label="Search and filter notices"
          className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs space-y-4"
        >
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
          <DepartmentFilter
            departments={DEPARTMENTS}
            selectedDepartment={selectedDepartment}
            onSelectDepartment={setSelectedDepartment}
          />
        </section>

        {/* Selected Notice Preview Banner (Week 5 placeholder for View Notice action) */}
        {selectedNotice && (
          <div
            role="status"
            className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-start justify-between gap-4"
          >
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" aria-hidden="true" />
              <div className="text-sm space-y-1">
                <p className="font-semibold text-emerald-950">
                  Selected: {selectedNotice.title}
                </p>
                <p className="text-emerald-800 text-xs">
                  Department: {selectedNotice.department} · Category: {selectedNotice.category} · Published: {selectedNotice.publishedDate}
                  {selectedNotice.deadline ? ` · Deadline: ${selectedNotice.deadline}` : ''}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setSelectedNotice(null)}
              aria-label="Close selected notice preview"
              className="p-1 rounded-md text-emerald-700 hover:bg-emerald-100 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Results Count */}
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium" aria-live="polite">
          <span>
            Showing {filteredNotices.length} of {MOCK_NOTICES.length} sample notices
          </span>
          {(searchQuery || selectedDepartment !== 'All') && (
            <button
              type="button"
              onClick={handleResetFilters}
              className="text-emerald-700 hover:text-emerald-900 underline cursor-pointer"
            >
              Reset filters
            </button>
          )}
        </div>

        {/* Notice Grid or Empty State */}
        {filteredNotices.length > 0 ? (
          <section
            aria-label="Notice list"
            className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5"
          >
            {filteredNotices.map((notice) => (
              <NoticeCard
                key={notice.id}
                notice={notice}
                onViewNotice={setSelectedNotice}
              />
            ))}
          </section>
        ) : (
          <section
            aria-label="No matching notices"
            className="bg-white rounded-xl border border-dashed border-slate-300 p-10 text-center space-y-3"
          >
            <FileSearch className="w-10 h-10 text-slate-400 mx-auto" aria-hidden="true" />
            <h2 className="text-base font-semibold text-slate-900">
              No matching notices found
            </h2>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              No notices matched your current search query
              {selectedDepartment !== 'All' ? ` in ${selectedDepartment}` : ''}. Try adjusting your keywords or selecting another department.
            </p>
            <button
              type="button"
              onClick={handleResetFilters}
              className="inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-800 text-white hover:bg-emerald-900 transition-colors cursor-pointer"
            >
              Clear search &amp; filters
            </button>
          </section>
        )}
      </div>
    </Layout>
  )
}
