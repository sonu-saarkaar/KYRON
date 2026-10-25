import React, { useState } from 'react';
import {
  MessageCircle,
  Instagram,
  Eye,
  Sparkles,
  Send,
  CheckCircle2,
  Clock,
  ArrowRight,
  User,
  ShieldCheck,
  Bot
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MacSocialCard({
  action,
  onReplyCustom,
  onSmartReply,
  onAutoReplyInstagram
}) {
  const [replyContact, setReplyContact] = useState('');
  const [replyText, setReplyText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // WHATSAPP PEEK & UNREAD SUMMARY CARD
  if (
    action?.action === 'WHATSAPP_PEEK' ||
    action?.action === 'WHATSAPP_UNREAD_SUMMARY' ||
    action?.type === 'whatsapp_peek'
  ) {
    const chats = action.result?.chats || action.chats || [];
    const totalCount = action.result?.unread_count ?? action.unread_count ?? chats.length;

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-[#0e1a2d]/95 via-[#112338]/90 to-[#141b2a]/95 border border-emerald-500/40 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <MessageCircle className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                <span>Real WhatsApp Unread Audit</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                  Live macOS DB
                </span>
              </h4>
              <span className="text-[10px] text-slate-400">
                Authentic messages scanned directly from macOS WhatsApp
              </span>
            </div>
          </div>

          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-500/30">
            {totalCount} Unread
          </span>
        </div>

        {/* Empty state */}
        {chats.length === 0 ? (
          <div className="p-3 text-center rounded-xl bg-black/20 border border-white/5 my-2 text-slate-300 text-xs">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
            <span>Abhi koi naya ya unread message nahi hai. Sabhi chats up-to-date hain!</span>
          </div>
        ) : (
          /* Messages List */
          <div className="space-y-2 mb-3">
            {chats.map((c, idx) => (
              <div
                key={c.id || idx}
                className="p-2.5 rounded-xl border bg-black/30 border-white/10 hover:border-emerald-500/30 transition"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1.5">
                    <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-emerald-400 to-teal-500 flex items-center justify-center text-[10px] font-bold text-slate-950">
                      {(c.sender || 'U')[0]}
                    </div>
                    <span className="text-xs font-bold text-slate-200">
                      {c.sender}
                    </span>
                    <span className="text-[9px] text-emerald-400 font-mono font-bold bg-emerald-950/60 px-1.5 py-0.2 rounded">
                      {c.unread_count} new
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-white/5 my-1.5">
                  "{c.preview}"
                </p>

                <div className="flex items-center justify-end gap-1.5 pt-1">
                  <button
                    onClick={() => {
                      setReplyContact(c.sender);
                      setIsTyping(true);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[10px] font-semibold border border-emerald-500/30 transition flex items-center gap-1"
                  >
                    <Send className="w-2.5 h-2.5" />
                    <span>Reply to {c.sender}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Inline custom reply form */}
        {isTyping && (
          <div className="p-2.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-emerald-300">
                Replying to: {replyContact}
              </span>
              <button
                onClick={() => setIsTyping(false)}
                className="text-[10px] text-slate-400 hover:text-white"
              >
                Cancel
              </button>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder={`Type reply to ${replyContact}...`}
                className="flex-1 px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && replyText.trim()) {
                    onReplyCustom?.(replyContact, replyText.trim());
                    setIsTyping(false);
                    setReplyText('');
                  }
                }}
              />
              <button
                onClick={() => {
                  if (replyText.trim()) {
                    onReplyCustom?.(replyContact, replyText.trim());
                    setIsTyping(false);
                    setReplyText('');
                  }
                }}
                className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-xs font-bold transition flex items-center gap-1"
              >
                <Send className="w-3 h-3" />
                <span>Send</span>
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // WHATSAPP DISAMBIGUATION CARD (Multiple contacts found e.g. Sonu 2, Sonu Bhai)
  if (action?.action === 'WHATSAPP_DISAMBIGUATION') {
    const candidates = action.result?.candidates || action.candidates || [];
    const query = action.result?.query || action.query || 'Contact';

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-amber-950/50 via-slate-900 to-[#121824] border border-amber-500/40 text-xs shadow-2xl">
        <div className="flex items-center justify-between mb-2.5 pb-2 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
              <User className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-amber-300">
                Multiple Contacts Found for "{query}"
              </h4>
              <span className="text-[10px] text-slate-400">
                Click a contact or speak their name to select
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded-full border border-amber-500/40">
            {candidates.length} Matches
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 my-2">
          {candidates.map((c, i) => (
            <button
              key={i}
              onClick={() => onReplyCustom?.(c.name, action.result?.message_pending || '')}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-amber-500/20 border border-white/10 hover:border-amber-400/50 text-left transition flex items-center justify-between group"
            >
              <div>
                <span className="text-xs font-bold text-slate-200 group-hover:text-amber-200 block">
                  {c.name}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {c.raw_phone || c.phone || 'WhatsApp Contact'}
                </span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-amber-300 group-hover:translate-x-0.5 transition" />
            </button>
          ))}
        </div>
      </div>
    );
  }

  // WHATSAPP AWAITING MESSAGE CARD
  if (action?.action === 'WHATSAPP_AWAITING_MESSAGE') {
    const contact = action.result?.contact || action.contact;
    const name = contact?.name || 'Contact';
    const phone = contact?.raw_phone || contact?.phone || '';

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-cyan-950/40 via-slate-900 to-[#101824] border border-cyan-500/40 text-xs shadow-xl">
        <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
              <MessageCircle className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-cyan-300">
                Contact Ready: {name}
              </h4>
              <span className="text-[10px] text-slate-400 font-mono">
                {phone}
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-500/30">
            Awaiting Message
          </span>
        </div>
        <p className="text-[11px] text-slate-300 mt-1">
          Aap mic me bolein: <strong className="text-white">"bolo kal subah meeting hai"</strong> ya niche message likh kar bhejein.
        </p>
      </div>
    );
  }

  // WHATSAPP MESSAGE SENT CARD
  if (action?.action === 'WHATSAPP_MESSAGE_SENT') {
    const contact = action.result?.contact || action.contact;
    const name = contact?.name || action.result?.name || 'Contact';
    const message = action.result?.message || action.message || '';

    return (
      <div className="mt-3 p-3 rounded-2xl bg-emerald-950/40 border border-emerald-500/50 text-xs shadow-xl">
        <div className="flex items-center justify-between mb-1.5 pb-1.5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <span className="font-bold text-emerald-300">Message Delivered to {name}</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-500/30">
            Delivered
          </span>
        </div>
        <p className="text-[11px] text-slate-200 bg-black/40 p-2 rounded-lg border border-white/5 my-1">
          "{message}"
        </p>
        <span className="text-[10px] text-cyan-300 block font-mono">
          ✓ Opened via WhatsApp on Mac & Dispatched
        </span>
      </div>
    );
  }

  // INSTAGRAM AUTO-REPLY CARD
  if (action?.action === 'INSTAGRAM_AUTO_REPLY' || action?.type === 'instagram_auto_reply') {
    const replies = action.result?.replies || action.replies || [];

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-[#181128]/95 via-[#231538]/90 to-[#120f1e]/95 border border-pink-500/40 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-pink-500/20 border border-pink-500/30 flex items-center justify-center">
              <Instagram className="w-4 h-4 text-pink-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-pink-300 flex items-center gap-1.5">
                <span>Instagram DMs Auto-Responder</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-pink-500/20 text-pink-300 border border-pink-500/30 font-mono">
                  Live Broadcast
                </span>
              </h4>
              <span className="text-[10px] text-slate-400">
                All incoming direct messages answered and spoken out loud
              </span>
            </div>
          </div>

          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-500/30">
            ✓ Complete
          </span>
        </div>

        <div className="space-y-2">
          {replies.map((r, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-black/30 border border-pink-500/20 flex flex-col gap-1 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-pink-300 flex items-center gap-1">
                  <span>@{r.user}</span>
                </span>
                <span className="text-[10px] font-mono text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Dispatched & Vocalized</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-200 bg-pink-950/40 p-2 rounded-lg border border-pink-500/20">
                "{r.reply}"
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // WHATSAPP CUSTOM REPLY CONFIRMATION CARD
  if (action?.action === 'WHATSAPP_CUSTOM_REPLY') {
    return (
      <div className="mt-3 p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 text-xs">
        <div className="flex items-center justify-between mb-1">
          <span className="font-bold text-emerald-300 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>WhatsApp Message Dispatched</span>
          </span>
          <span className="text-[10px] font-mono text-slate-400">
            To: {action.result?.contact || action.contact}
          </span>
        </div>
        <p className="text-[11px] text-slate-200 bg-black/30 p-2 rounded-lg border border-white/5">
          "{action.result?.message || action.message}"
        </p>
      </div>
    );
  }

  // WHATSAPP OPENED CARD
  if (action?.action === 'WHATSAPP_OPENED' || action?.type === 'whatsapp_opened') {
    return (
      <div className="mt-3 p-3 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 text-xs shadow-lg">
        <div className="flex items-center justify-between mb-1">
          <span className="font-bold text-emerald-300 flex items-center gap-1.5">
            <MessageCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>WhatsApp Application Active</span>
          </span>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-500/30">
            macOS Desktop Ready
          </span>
        </div>
        <p className="text-[11px] text-slate-300 mt-1">
          WhatsApp is launched and focused. Speak your next directive: <strong className="text-cyan-300">"Kyron Sonu search karo aur usko message karo Hi Sonu"</strong>.
        </p>
      </div>
    );
  }

  // WHATSAPP SEARCH AND SEND CARD
  if (action?.action === 'WHATSAPP_SEARCH_AND_SEND' || action?.type === 'whatsapp_search_and_send') {
    const contact = action.result?.contact || action.contact || 'Sonu';
    const message = action.result?.message || action.message || 'Hi Sonu';

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-emerald-950/60 via-[#102030]/80 to-slate-900 border border-emerald-500/50 text-xs shadow-2xl">
        <div className="flex items-center justify-between mb-2 pb-2 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-emerald-300">
                Message Delivered: {contact}
              </h4>
              <span className="text-[10px] text-slate-400">
                WhatsApp Search via Cmd+F & Dispatched on macOS Desktop
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-900/60 px-2 py-0.5 rounded-full border border-emerald-500/40">
            ✓ Sent
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 my-1">
          <span className="text-[10px] text-slate-400 font-mono block mb-0.5">
            Content sent to {contact}:
          </span>
          <p className="text-xs font-semibold text-white">
            "{message}"
          </p>
        </div>

        <div className="flex items-center justify-between mt-2 pt-1 text-[10px] text-slate-400 font-mono">
          <span className="text-cyan-300">🔔 macOS Desktop Notification Displayed</span>
          <span className="text-purple-300">🔊 Vocalized by OBG</span>
        </div>
      </div>
    );
  }

  // WHATSAPP SMART REPLY CONFIRMATION CARD
  if (action?.action === 'WHATSAPP_SMART_REPLY') {
    const replies = action.result?.replies || action.replies || [];
    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-cyan-950/40 border border-cyan-500/40 text-xs">
        <div className="flex items-center justify-between mb-2">
          <span className="font-bold text-cyan-300 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Autonomous Memory Replies Dispatched</span>
          </span>
          <span className="text-[10px] font-mono text-emerald-400 font-bold">
            ✓ {replies.length} Contacts
          </span>
        </div>
        <div className="space-y-1.5">
          {replies.map((r, i) => (
            <div key={i} className="p-2 rounded-lg bg-black/30 border border-white/5">
              <span className="text-[10px] font-bold text-slate-300 block mb-0.5">
                {r.contact}:
              </span>
              <p className="text-[11px] text-cyan-200">"{r.reply}"</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // WHATSAPP MULTI-REPLY CONFIRMATION CARD
  if (action?.action === 'WHATSAPP_MULTI_REPLY' || action?.type === 'whatsapp_multi_reply') {
    const results = action.result?.results || action.results || [];
    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-emerald-950/70 via-indigo-950/50 to-slate-900 border border-emerald-500/50 text-xs shadow-2xl">
        <div className="flex items-center justify-between mb-2 pb-2 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-emerald-300">
                WhatsApp Multi-Dispatch Sent
              </h4>
              <span className="text-[10px] text-slate-400">
                Directives executed sequentially on macOS desktop & synced
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-900/60 px-2 py-0.5 rounded-full border border-emerald-500/40">
            ✓ {results.length} Delivered
          </span>
        </div>

        <div className="space-y-1.5 my-1">
          {results.map((r, idx) => (
            <div key={idx} className="p-2.5 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-cyan-300 font-mono font-bold block">
                  To: {r.contact}
                </span>
                <p className="text-xs font-semibold text-white">
                  "{r.message}"
                </p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Sent</span>
              </span>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between mt-2 pt-1 text-[10px] text-slate-400 font-mono">
          <span className="text-cyan-300">🔔 Desktop Banners Posted</span>
          <span className="text-purple-300">🔊 Vocalized by OBG</span>
        </div>
      </div>
    );
  }

  // WHATSAPP UNREAD SUMMARY CARD
  if (action?.action === 'WHATSAPP_UNREAD_SUMMARY' || action?.type === 'whatsapp_unread_summary') {
    const chats = action.result?.chats || action.chats || [];
    const count = action.result?.unread_count || action.unread_count || chats.length;

    return (
      <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-[#0e1a2d]/95 via-[#112338]/90 to-[#141b2a]/95 border border-emerald-500/40 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
              <MessageCircle className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                <span>WhatsApp Unread Check</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                  Real SQLite Sync
                </span>
              </h4>
              <span className="text-[10px] text-slate-400">
                Audited unread chats without opening individual windows
              </span>
            </div>
          </div>

          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
            {count} Unread Messages
          </span>
        </div>

        <div className="space-y-2 mb-3">
          {chats.map((c, i) => (
            <div key={i} className="p-2.5 rounded-xl bg-black/30 border border-white/10 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200">
                  {c.sender}
                </span>
                <span className="text-[9px] text-emerald-400 font-mono font-bold bg-emerald-950/60 px-1.5 py-0.2 rounded">
                  {c.unread_count} New
                </span>
              </div>
              <p className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                "{c.preview}"
              </p>
            </div>
          ))}
        </div>

        <div className="flex items-center gap-2 pt-1 border-t border-white/10">
          <button
            onClick={() => onSmartReply?.()}
            className="flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:opacity-95 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-lg shadow-cyan-900/30 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span>Respond via Sonu's Memory</span>
          </button>
        </div>
      </div>
    );
  }

  return null;
}
