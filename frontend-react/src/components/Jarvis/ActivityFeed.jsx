import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  Brain,
  Zap,
  Terminal,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  Globe,
  Monitor,
} from 'lucide-react';

/**
 * ActivityFeed Component (Left Panel)
 * Real-time streaming telemetry and agent activity feed.
 * Pulls and displays live operations from Memory, Skills, CodeAgent, Cron, and System.
 */
export default function ActivityFeed({ events = [], onClear, isOpen = true, onToggle }) {
  const [filter, setFilter] = useState('ALL');
  const feedEndRef = useRef(null);

  const filteredEvents = events.filter((e) => {
    if (filter === 'ALL') return true;
    return e.type === filter;
  });

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const getEventIcon = (type, status) => {
    switch (type) {
      case 'MEMORY':
        return <Brain className="w-3.5 h-3.5 text-purple-400" />;
      case 'SKILLS':
        return <Zap className="w-3.5 h-3.5 text-amber-400" />;
      case 'CODE_AGENT':
        return <Terminal className="w-3.5 h-3.5 text-cyan-400" />;
      case 'BROWSER':
        return <Globe className="w-3.5 h-3.5 text-blue-400" />;
      case 'SYSTEM':
        return <Monitor className="w-3.5 h-3.5 text-teal-400" />;
      case 'CRON':
        return <Clock className="w-3.5 h-3.5 text-sky-400" />;
      default:
        return status === 'error' ? (
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
        ) : (
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
        );
    }
  };

  const getBadgeColor = (type) => {
    switch (type) {
      case 'MEMORY':
        return 'bg-purple-950/60 text-purple-300 border-purple-800/40';
      case 'SKILLS':
        return 'bg-amber-950/60 text-amber-300 border-amber-800/40';
      case 'CODE_AGENT':
        return 'bg-cyan-950/60 text-cyan-300 border-cyan-800/40';
      case 'BROWSER':
        return 'bg-blue-950/60 text-blue-300 border-blue-800/40';
      case 'SYSTEM':
        return 'bg-teal-950/60 text-teal-300 border-teal-800/40';
      case 'CRON':
        return 'bg-sky-950/60 text-sky-300 border-sky-800/40';
      default:
        return 'bg-slate-800/60 text-slate-300 border-slate-700/40';
    }
  };

  return (
    <aside
      className={`relative flex flex-col h-full bg-[#080d1a]/95 border-r border-cyan-900/30 backdrop-blur-xl transition-all duration-300 ${
        isOpen ? 'w-80' : 'w-12'
      }`}
    >
      {/* Panel Header */}
      <div className="flex items-center justify-between p-3 border-b border-cyan-900/30">
        <div className="flex items-center gap-2 overflow-hidden">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse shrink-0" />
          {isOpen && (
            <div>
              <h3 className="font-mono text-xs uppercase tracking-wider text-cyan-100 font-bold">
                Live Agent Feed
              </h3>
              <p className="text-[10px] text-cyan-400/60 font-mono">Real-time telemetry stream</p>
            </div>
          )}
        </div>

        <button
          onClick={onToggle}
          title={isOpen ? 'Collapse panel' : 'Expand panel'}
          className="p-1 rounded text-cyan-400/70 hover:text-cyan-200 hover:bg-cyan-950/40 transition-colors"
        >
          {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {isOpen && (
        <>
          {/* Quick Filters */}
          <div className="flex items-center gap-1 p-2 bg-slate-950/40 border-b border-cyan-950/30 overflow-x-auto text-[10px] font-mono">
            {['ALL', 'CODE_AGENT', 'SKILLS', 'MEMORY', 'CRON'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-0.5 rounded transition-all whitespace-nowrap ${
                  filter === f
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Events Stream */}
          <div className="flex-1 overflow-y-auto p-2.5 space-y-2 font-mono scrollbar-thin scrollbar-thumb-cyan-950">
            {filteredEvents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-4 text-slate-500 text-xs">
                <Activity className="w-6 h-6 mb-2 opacity-30 text-cyan-400" />
                <p>Telemetry stream ready.</p>
                <p className="text-[10px] mt-1 text-slate-600">Events will stream as agent reasons & executes.</p>
              </div>
            ) : (
              <AnimatePresence initial={false}>
                {filteredEvents.map((event) => (
                  <motion.div
                    key={event.id || `${event.timestamp}-${Math.random()}`}
                    initial={{ opacity: 0, y: -6, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="p-2 rounded bg-slate-900/60 border border-cyan-950/40 hover:border-cyan-500/30 transition-all text-xs"
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <div className="flex items-center gap-1.5">
                        {getEventIcon(event.type, event.status)}
                        <span
                          className={`text-[9px] px-1.5 py-0.2 rounded border font-semibold ${getBadgeColor(
                            event.type
                          )}`}
                        >
                          {event.type}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {event.time || new Date().toLocaleTimeString()}
                      </span>
                    </div>

                    <p className="text-slate-300 text-[11px] leading-relaxed break-words font-sans">
                      {event.message}
                    </p>

                    {event.detail && (
                      <p className="mt-1 text-[10px] text-cyan-400/70 bg-black/40 px-1.5 py-0.5 rounded truncate font-mono">
                        {event.detail}
                      </p>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
            <div ref={feedEndRef} />
          </div>

          {/* Footer stats */}
          <div className="p-2 border-t border-cyan-900/30 flex items-center justify-between text-[10px] text-slate-500 font-mono">
            <span>{filteredEvents.length} events logged</span>
            {onClear && (
              <button
                onClick={onClear}
                className="flex items-center gap-1 hover:text-cyan-400 transition-colors"
                title="Clear feed"
              >
                <RotateCcw className="w-3 h-3" />
                Clear
              </button>
            )}
          </div>
        </>
      )}
    </aside>
  );
}
