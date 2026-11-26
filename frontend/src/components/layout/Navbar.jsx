import { useState } from 'react'
import { BookOpen, CalendarClock, Menu, ShieldCheck, X } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'archive', label: 'Notice Archive', icon: BookOpen, active: true },
  { id: 'deadlines', label: 'Deadlines', icon: CalendarClock, active: false },
]

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="bg-emerald-900 text-white shadow-sm border-b border-emerald-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-700 border border-emerald-500/60 flex items-center justify-center font-bold text-lg tracking-wider text-white">
              IR
            </div>
            <div>
              <span className="block text-lg font-bold leading-tight tracking-tight">
                IRIS
              </span>
              <span className="block text-xs text-emerald-200 leading-tight">
                IUT Repository &amp; Information System
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav aria-label="Main navigation" className="hidden md:flex items-center gap-2">
            {NAV_ITEMS.map(({ id, label, icon: Icon, active }) => (
              <a
                key={id}
                href={`#${id}`}
                aria-current={active ? 'page' : undefined}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-emerald-800 text-white'
                    : 'text-emerald-100 hover:bg-emerald-800/60 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </a>
            ))}
          </nav>

          {/* Right Badge & Mobile Toggle */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium bg-emerald-950/60 px-3 py-1.5 rounded-full border border-emerald-700 text-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              @iut-dhaka.edu
            </span>

            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
              className="md:hidden p-2 rounded-lg text-emerald-100 hover:bg-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-400 cursor-pointer"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav
            aria-label="Mobile navigation"
            className="md:hidden py-3 border-t border-emerald-800 space-y-1"
          >
            {NAV_ITEMS.map(({ id, label, icon: Icon, active }) => (
              <a
                key={id}
                href={`#${id}`}
                onClick={() => setMobileMenuOpen(false)}
                aria-current={active ? 'page' : undefined}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
                  active
                    ? 'bg-emerald-800 text-white'
                    : 'text-emerald-100 hover:bg-emerald-800/60'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </a>
            ))}
          </nav>
        )}
      </div>
    </header>
  )
}

