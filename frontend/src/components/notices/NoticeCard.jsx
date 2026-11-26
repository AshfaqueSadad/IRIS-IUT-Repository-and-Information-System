import { ArrowRight, Building2, Calendar, Clock, Tag } from 'lucide-react'

export default function NoticeCard({ notice, onViewNotice }) {
  const { title, category, department, publishedDate, description, deadline } = notice

  return (
    <article className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-emerald-400 transition-colors flex flex-col justify-between gap-4">
      <div className="space-y-3">
        {/* Top Metadata Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
              <Tag className="w-3 h-3" aria-hidden="true" />
              {category}
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
              <Building2 className="w-3 h-3" aria-hidden="true" />
              {department}
            </span>
          </div>

          {deadline && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              <Clock className="w-3 h-3" aria-hidden="true" />
              Due: {deadline}
            </span>
          )}
        </div>

        {/* Title */}
        <h2 className="text-base sm:text-lg font-semibold text-slate-900 leading-snug">
          {title}
        </h2>

        {/* Optional Description */}
        {description && (
          <p className="text-sm text-slate-600 leading-relaxed line-clamp-2">
            {description}
          </p>
        )}
      </div>

      {/* Footer: Publication Date & View Notice Action */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
          <Calendar className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
          Published {publishedDate}
        </span>

        <button
          type="button"
          onClick={() => onViewNotice?.(notice)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-800 hover:text-emerald-950 bg-emerald-50 hover:bg-emerald-100 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          View Notice
          <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
        </button>
      </div>
    </article>
  )
}

