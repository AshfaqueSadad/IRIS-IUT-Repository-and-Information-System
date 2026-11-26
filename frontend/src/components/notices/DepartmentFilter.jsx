import { Building2 } from 'lucide-react'

export default function DepartmentFilter({
  departments,
  selectedDepartment,
  onSelectDepartment,
}) {
  return (
    <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Filter by department">
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 mr-1">
        <Building2 className="w-3.5 h-3.5" aria-hidden="true" />
        Department:
      </span>

      {departments.map((dept) => {
        const isSelected = selectedDepartment === dept
        return (
          <button
            key={dept}
            type="button"
            onClick={() => onSelectDepartment(dept)}
            aria-pressed={isSelected}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
              isSelected
                ? 'bg-emerald-800 text-white border-emerald-800 shadow-xs'
                : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
            }`}
          >
            {dept}
          </button>
        )
      })}
    </div>
  )
}

