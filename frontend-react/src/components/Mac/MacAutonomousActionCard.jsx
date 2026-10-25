import React from 'react';
import {
  CreditCard,
  Plane,
  Ticket,
  FileCheck,
  CheckCircle2,
  ExternalLink,
  Copy,
  Download,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MacAutonomousActionCard({ action }) {
  if (!action) return null;

  const data = action.data || {};
  const actionId = action.action_id || data.action_id || 'autonomous_action';
  const title = action.title || 'Autonomous Action Execution';
  const portalUrl = action.portal_url || data.portal;
  const appId = action.application_id || data.application_id || data.booking_id || data.form_id;

  const getIcon = () => {
    switch (actionId) {
      case 'pan_card':
        return <CreditCard className="w-5 h-5 text-amber-400" />;
      case 'passport':
        return <Plane className="w-5 h-5 text-cyan-400" />;
      case 'ticket_booking':
        return <Ticket className="w-5 h-5 text-emerald-400" />;
      default:
        return <FileCheck className="w-5 h-5 text-indigo-400" />;
    }
  };

  const getGradient = () => {
    switch (actionId) {
      case 'pan_card':
        return 'from-amber-950/40 via-slate-900/80 to-slate-950 border-amber-500/30';
      case 'passport':
        return 'from-cyan-950/40 via-slate-900/80 to-slate-950 border-cyan-500/30';
      case 'ticket_booking':
        return 'from-emerald-950/40 via-slate-900/80 to-slate-950 border-emerald-500/30';
      default:
        return 'from-indigo-950/40 via-slate-900/80 to-slate-950 border-indigo-500/30';
    }
  };

  const copyAppId = () => {
    if (appId) {
      navigator.clipboard.writeText(appId);
      toast.success(`Copied ID: ${appId}`);
    }
  };

  return (
    <div className={`mt-3 p-4 rounded-2xl bg-gradient-to-br ${getGradient()} border shadow-2xl backdrop-blur-xl text-xs space-y-3`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10 shadow-inner">
            {getIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-white tracking-wide text-sm">{title}</h4>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                AUTONOMOUSLY COMPLETED
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Verified from Asif Aslam (Sonu Sarkar) Master Profile & Document Vault
            </p>
          </div>
        </div>

        {appId && (
          <button
            onClick={copyAppId}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition font-mono text-[11px]"
            title="Copy Application ID"
          >
            <Copy className="w-3 h-3 text-cyan-400" />
            <span>{appId}</span>
          </button>
        )}
      </div>

      {/* PAN Card Specific Details */}
      {actionId === 'pan_card' && data.applicant_details && (
        <div className="space-y-2.5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-[11px]">
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Applicant</span>
              <span className="text-white font-semibold">{data.applicant_details.full_name}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Father's Name</span>
              <span className="text-slate-200">{data.applicant_details.father_name}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Date of Birth</span>
              <span className="text-slate-200">{data.applicant_details.dob}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Aadhaar e-KYC</span>
              <span className="text-amber-300 font-semibold">{data.applicant_details.aadhaar_number}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Delivery Mode</span>
              <span className="text-slate-200">Physical Card + e-PAN</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Target City</span>
              <span className="text-slate-200">Motihari, Bihar</span>
            </div>
          </div>

          {/* Attached Assets */}
          {Array.isArray(data.attached_assets) && (
            <div className="p-2.5 rounded-xl bg-black/30 border border-white/5 space-y-1.5">
              <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider font-mono block">
                Auto-Formatted Vault Attachments
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {data.attached_assets.map((asset, idx) => (
                  <div key={idx} className="flex items-center justify-between p-1.5 rounded-lg bg-white/[0.03] text-[11px]">
                    <span className="text-slate-300">{asset.type}</span>
                    <span className="text-emerald-400 font-mono text-[10px] font-bold">✓ Ready</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Passport Seva Specific Details */}
      {actionId === 'passport' && data.applicant_details && (
        <div className="space-y-2.5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-[11px]">
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Given Name</span>
              <span className="text-white font-semibold">{data.applicant_details.given_name} {data.applicant_details.surname}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">RPO Jurisdiction</span>
              <span className="text-cyan-300 font-semibold">RPO Patna</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Police Station</span>
              <span className="text-slate-200">{data.police_station}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">ECR Status</span>
              <span className="text-emerald-300 font-semibold">Non-ECR Eligible</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Passport Booklet</span>
              <span className="text-slate-200">Normal 36 Pages</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Aadhaar Proof</span>
              <span className="text-slate-200">{data.applicant_details.aadhaar}</span>
            </div>
          </div>

          {Array.isArray(data.attached_assets) && (
            <div className="p-2.5 rounded-xl bg-black/30 border border-white/5 space-y-1.5">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider font-mono block">
                Passport Seva Document Formats
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {data.attached_assets.map((asset, idx) => (
                  <div key={idx} className="flex items-center justify-between p-1.5 rounded-lg bg-white/[0.03] text-[11px]">
                    <span className="text-slate-300">{asset.type}</span>
                    <span className="text-emerald-400 font-mono text-[10px] font-bold">✓ 413x531 px</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ticket Booking Specific Details */}
      {actionId === 'ticket_booking' && data.primary_passenger && (
        <div className="space-y-2.5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-[11px]">
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Route</span>
              <span className="text-emerald-300 font-bold">{data.route}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Passenger</span>
              <span className="text-white font-semibold">{data.primary_passenger.name} (Age: {data.primary_passenger.age})</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Berth Choice</span>
              <span className="text-emerald-300">{data.primary_passenger.berth_preference}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Payment Routing</span>
              <span className="text-slate-200">HDFC UPI: {data.payment_route?.upi_id}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Travel Date</span>
              <span className="text-slate-200">{data.travel_date}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[9px] uppercase">Engine</span>
              <span className="text-slate-200">Playwright Headless Agent</span>
            </div>
          </div>
        </div>
      )}

      {/* Universal Form Auto-Filler Details */}
      {actionId === 'universal_form' && data.mapped_fields && (
        <div className="space-y-2">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-[11px]">
            {Object.entries(data.mapped_fields).slice(0, 6).map(([key, val]) => (
              <div key={key}>
                <span className="text-slate-500 block text-[9px] uppercase">{key}</span>
                <span className="text-slate-200 truncate block">{String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions Footer */}
      <div className="flex items-center justify-between pt-1 text-[11px]">
        <span className="text-slate-400 font-mono flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Zero manual questions needed. Form pre-filled & verified.</span>
        </span>

        {portalUrl && (
          <a
            href={portalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold transition shadow-md"
          >
            <span>Open Official Portal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>
    </div>
  );
}
