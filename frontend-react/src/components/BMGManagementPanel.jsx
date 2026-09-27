import { useState } from 'react';
import {
  ArrowDownRight,
  ArrowUpRight,
  Briefcase,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Layers3,
  MoreHorizontal,
  Plus,
  Target,
  Users
} from 'lucide-react';

const projects = [
  { name: 'Northstar rebrand', team: 'Brand & Creative', progress: 78, due: 'Oct 04', budget: '$42,800', color: 'bg-violet-500' },
  { name: 'Q4 growth campaign', team: 'Marketing', progress: 54, due: 'Oct 12', budget: '$68,250', color: 'bg-cyan-500' },
  { name: 'Client portal refresh', team: 'Product', progress: 32, due: 'Oct 21', budget: '$91,600', color: 'bg-amber-500' }
];

const meetings = [
  { time: '09:30', period: 'AM', title: 'Leadership stand-up', detail: 'Boardroom · 6 attendees', color: 'bg-violet-400' },
  { time: '11:00', period: 'AM', title: 'Northstar project review', detail: 'Design team · 45 min', color: 'bg-cyan-400' },
  { time: '02:15', period: 'PM', title: 'Quarterly client check-in', detail: 'Video call · 30 min', color: 'bg-amber-400' }
];

export default function BMGManagementPanel() {
  const [activeSubTab, setActiveSubTab] = useState('operations');

  const tabs = [
    { id: 'operations', label: 'Operations Management' },
    { id: 'social', label: 'Social Media Management' },
    { id: 'support', label: 'Support' },
    { id: 'business', label: 'Business Analysis Management' }
  ];

  return (
    <main id="bmg-panel" role="tabpanel" aria-labelledby="bmg-tab" tabIndex={0} className="flex-1 min-h-0 overflow-y-auto bg-[#0a0c12] text-slate-100">
      <div className="min-h-full bg-[radial-gradient(ellipse_at_top_right,rgba(91,63,164,0.17),transparent_36%)]">
        <div className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8 lg:py-9">
          
          {/* Sub Navigation */}
          <nav className="mb-8 flex gap-4 border-b border-white/10 pb-2 overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`whitespace-nowrap px-4 py-2 text-sm font-semibold transition-colors ${
                  activeSubTab === tab.id
                    ? 'text-violet-400 border-b-2 border-violet-400'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <div className="mb-3 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-violet-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
                BMG · {tabs.find(t => t.id === activeSubTab)?.label}
              </div>
              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Good morning, Alex.</h1>
              <p className="mt-2 text-sm text-slate-400">Here&apos;s the overview of your business today.</p>
            </div>
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <button type="button" className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-white/[0.08]">
                Export report
              </button>
              <button type="button" className="inline-flex items-center gap-2 rounded-xl bg-violet-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-950/40 hover:bg-violet-400">
                <Plus className="h-4 w-4" />
                New project
              </button>
            </div>
          </section>

          {activeSubTab === 'operations' && (
            <>
              <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              { title: 'Total revenue', value: '$284,590', delta: '+12.8%', sub: 'vs. last month', icon: CircleDollarSign, trend: 'up', color: 'text-emerald-300 bg-emerald-400/10' },
              { title: 'Active projects', value: '18', delta: '+3', sub: 'since last month', icon: Briefcase, trend: 'up', color: 'text-violet-300 bg-violet-400/10' },
              { title: 'Team utilization', value: '84.6%', delta: '-2.4%', sub: 'vs. last month', icon: Users, trend: 'down', color: 'text-cyan-300 bg-cyan-400/10' },
              { title: 'On-time delivery', value: '96.2%', delta: '+4.1%', sub: 'quarter to date', icon: Target, trend: 'up', color: 'text-amber-300 bg-amber-400/10' }
            ].map(({ title, value, delta, sub, icon: Icon, trend, color }) => (
              <article key={title} className="rounded-2xl border border-white/[0.08] bg-[#11141d]/90 p-5 shadow-[0_10px_40px_rgba(0,0,0,0.12)]">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">{title}</span>
                  <span className={`rounded-xl p-2.5 ${color}`}><Icon className="h-5 w-5" /></span>
                </div>
                <div className="mt-5 flex items-end justify-between gap-2">
                  <span className="text-3xl font-semibold tracking-tight">{value}</span>
                  <span className={`mb-1 inline-flex items-center gap-1 text-xs font-semibold ${trend === 'up' ? 'text-emerald-300' : 'text-rose-300'}`}>
                    {trend === 'up' ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                    {delta}
                  </span>
                </div>
                <p className="mt-2 text-xs text-slate-500">{sub}</p>
              </article>
            ))}
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.6fr_1fr]">
            <article className="rounded-2xl border border-white/[0.08] bg-[#11141d]/90 p-5 sm:p-6">
              <div className="mb-6 flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Layers3 className="h-5 w-5 text-violet-300" />
                    <h2 className="text-lg font-semibold">Project portfolio</h2>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">Progress across your active work.</p>
                </div>
                <button type="button" aria-label="More project options" className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-slate-300">
                  <MoreHorizontal className="h-5 w-5" />
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[620px] text-left">
                  <thead>
                    <tr className="border-b border-white/[0.07] text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                      <th className="pb-3 font-medium">Project</th>
                      <th className="pb-3 font-medium">Progress</th>
                      <th className="pb-3 font-medium">Due date</th>
                      <th className="pb-3 font-medium">Budget</th>
                      <th className="pb-3" />
                    </tr>
                  </thead>
                  <tbody>
                    {projects.map((project) => (
                      <tr key={project.name} className="border-b border-white/[0.05] last:border-0">
                        <td className="py-4 pr-4">
                          <div className="font-medium text-slate-200">{project.name}</div>
                          <div className="mt-1 text-xs text-slate-500">{project.team}</div>
                        </td>
                        <td className="w-40 py-4 pr-5">
                          <div className="mb-2 flex items-center justify-between text-xs">
                            <span className="text-slate-400">{project.progress}%</span>
                          </div>
                          <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.07]">
                            <div className={`h-full rounded-full ${project.color}`} style={{ width: `${project.progress}%` }} />
                          </div>
                        </td>
                        <td className="py-4 pr-4 text-sm text-slate-400">{project.due}</td>
                        <td className="py-4 pr-4 text-sm font-medium text-slate-300">{project.budget}</td>
                        <td className="py-4 text-right text-slate-500"><ChevronRight className="inline h-4 w-4" /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <button type="button" className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-violet-300 hover:text-violet-200">
                View all projects <ArrowUpRight className="h-4 w-4" />
              </button>
            </article>

            <article className="rounded-2xl border border-white/[0.08] bg-[#11141d]/90 p-5 sm:p-6">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <CalendarDays className="h-5 w-5 text-cyan-300" />
                    <h2 className="text-lg font-semibold">Today&apos;s agenda</h2>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">Tuesday, September 27</p>
                </div>
                <button type="button" aria-label="Open calendar" className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-slate-300">
                  <CalendarDays className="h-4 w-4" />
                </button>
              </div>
              <div className="space-y-1">
                {meetings.map((meeting) => (
                  <div key={meeting.title} className="flex gap-4 rounded-xl px-2 py-3 transition hover:bg-white/[0.03]">
                    <div className="w-14 shrink-0 text-right">
                      <div className="text-sm font-semibold text-slate-200">{meeting.time}</div>
                      <div className="text-[10px] text-slate-500">{meeting.period}</div>
                    </div>
                    <div className={`w-0.5 shrink-0 rounded-full ${meeting.color}`} />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-slate-200">{meeting.title}</div>
                      <div className="mt-1 text-xs text-slate-500">{meeting.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-5 flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.025] px-3 py-3">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Clock3 className="h-4 w-4 text-violet-300" />
                  Next meeting in 24 minutes
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-300" />
              </div>
            </article>
          </section>
            </>
          )}

          {activeSubTab !== 'operations' && (
            <div className="mt-8 flex min-h-[400px] items-center justify-center rounded-2xl border border-white/[0.08] bg-[#11141d]/50">
              <div className="text-center">
                <Layers3 className="mx-auto h-12 w-12 text-slate-600 mb-4" />
                <h3 className="text-xl font-semibold text-slate-300">
                  {tabs.find(t => t.id === activeSubTab)?.label}
                </h3>
                <p className="mt-2 text-sm text-slate-500">
                  This module is currently under development.
                </p>
                <button
                  type="button"
                  onClick={() => setActiveSubTab('operations')}
                  className="mt-6 rounded-xl bg-white/[0.04] px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/[0.08] transition-colors"
                >
                  Return to Operations
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
