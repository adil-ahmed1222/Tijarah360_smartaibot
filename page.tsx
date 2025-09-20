"use client";

import { useState, useRef, useEffect } from "react";
import { FiSend, FiGlobe } from "react-icons/fi";

interface Message {
  role: "user" | "assistant";
  content: string;
}

type Language = 'en' | 'ar';

interface Translation {
  title: string;
  fullChat: string;
  minimizeChat: string;
  greeting: string;
  thinking: string;
  placeholder: string;
  footer: string;
  suggestions: string[];
  autocomplete: string[];
}

interface Translations {
  en: Translation;
  ar: Translation;
}

const API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://127.0.0.1:8000/rag_chat";


// Translations with proper typing
const translations: Translations = {
  en: {
    title: "Tijarah360 AI Agent",
    fullChat: "USE FULL CHAT",
    minimizeChat: "MINIMIZE CHAT",
    greeting: "Hello! I'm T360 Musa, your smart assistant. Ask me anything",
    thinking: "Thinking…",
    placeholder: "Try it",
    footer: "Tijarah360 AI Agent is a chatbot that can answer questions and help you with your business.",
    suggestions: [
      "Is your POS system cloud-based",
      "Can I grow my business using your solutions",
      "Can I print receipts and manage inventory",
      "Does your POS support sales reports",
      "How can I manage my inventory"
    ],
    autocomplete: [
      "Is your POS system cloud-based",
      "Can I grow my business using your solutions", 
      "Can I print receipts and manage inventory",
      "Does your POS support sales reports",
      "How can I manage my inventory",
      "What payment methods do you support",
      "Can I track my sales performance",
      "How do I set up my POS system",
      "Can I manage multiple locations",
      "What are your pricing plans",
      "How do I contact customer support",
      "Can I integrate with accounting software",
      "Do you offer training for new users",
      "What security features do you have",
      "Can I customize receipts and invoices"
    ]
  },
  ar: {
    title: "وكيل تجارة 360 الذكي",
    fullChat: "استخدام الدردشة الكاملة",
    minimizeChat: "تصغير الدردشة",
    greeting: "مرحباً! أنا موسى T360، مساعدك الذكي. اسألني أي شيء",
    thinking: "أفكر...",
    placeholder: "جرب ذلك",
    footer: "وكيل تجارة 360 الذكي هو روبوت محادثة يمكنه الإجابة على الأسئلة ومساعدتك في عملك.",
    suggestions: [
      "هل نظام نقاط البيع الخاص بك قائم على السحابة",
      "هل يمكنني تنمية أعمالي باستخدام حلولكم",
      "هل يمكنني طباعة الإيصالات وإدارة المخزون",
      "هل يدعم نظام نقاط البيع تقارير المبيعات",
      "كيف يمكنني إدارة مخزوني"
    ],
    autocomplete: [
      "هل نظام نقاط البيع الخاص بك قائم على السحابة",
      "هل يمكنني تنمية أعمالي باستخدام حلولكم",
      "هل يمكنني طباعة الإيصالات وإدارة المخزون", 
      "هل يدعم نظام نقاط البيع تقارير المبيعات",
      "كيف يمكنني إدارة مخزوني",
      "ما هي طرق الدفع التي تدعمونها",
      "هل يمكنني تتبع أداء مبيعاتي",
      "كيف أقوم بإعداد نظام نقاط البيع",
      "هل يمكنني إدارة مواقع متعددة",
      "ما هي خطط التسعير الخاصة بكم",
      "كيف أتواصل مع دعم العملاء",
      "هل يمكنني التكامل مع برامج المحاسبة",
      "هل تقدمون تدريب للمستخدمين الجدد",
      "ما هي الميزات الأمنية التي لديكم",
      "هل يمكنني تخصيص الإيصالات والفواتير"
    ]
  }
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const [isMounted, setIsMounted] = useState(false);
  
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const t: Translation = translations[language];

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted) {
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, isMounted]);

  // Autocomplete logic
  useEffect(() => {
    if (isMounted && input.trim() && input.length > 1) {
      const filtered = t.autocomplete.filter(suggestion =>
        suggestion.toLowerCase().includes(input.toLowerCase())
      );
      setFilteredSuggestions(filtered.slice(0, 5));
      setShowAutocomplete(filtered.length > 0);
    } else {
      setShowAutocomplete(false);
      setFilteredSuggestions([]);
    }
    setActiveSuggestionIndex(-1);
  }, [input, t.autocomplete, isMounted]);

  const sendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    setShowAutocomplete(false);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.response || "(no response)" },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "⚠️ Failed to respond. Try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    setShowAutocomplete(false);
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  const handleAutocompleteClick = (suggestion: string) => {
    setInput(suggestion);
    setShowAutocomplete(false);
    inputRef.current?.focus();
  };

  const handleFullChatClick = () => {
    setIsFullScreen(!isFullScreen);
  };

  const handleLanguageToggle = () => {
    setLanguage(prev => prev === 'en' ? 'ar' : 'en');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showAutocomplete) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestionIndex(prev => 
        prev < filteredSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter' && activeSuggestionIndex >= 0) {
      e.preventDefault();
      handleAutocompleteClick(filteredSuggestions[activeSuggestionIndex]);
    } else if (e.key === 'Escape') {
      setShowAutocomplete(false);
      setActiveSuggestionIndex(-1);
    }
  };

  // Static classes for server rendering
  // const containerClasses = `min-h-screen bg-gray-50 flex items-center justify-center p-4 ${
  //   isMounted && isFullScreen ? 'p-0' : ''
  // }`;
  
  const chatBoxClasses = `w-full bg-white shadow-xl rounded-3xl flex flex-col relative overflow-hidden ${
    isMounted && isFullScreen ? 'max-w-none h-screen rounded-none' : 'max-w-4xl min-h-[80vh]'
  }`;

  return (
    <div 
      className={'min-h-screen bg-gray-50 flex items-center justify-center p-4'}
      dir={isMounted ? (language === 'ar' ? 'rtl' : 'ltr') : 'ltr'}
    >
      <div className={chatBoxClasses}>
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-100">
          <div className="text-lg font-semibold text-gray-800">
            {t.title}
          </div>
          {isMounted && (
            <div className="flex items-center gap-3">
              <button
                onClick={handleLanguageToggle}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-800 font-medium text-sm"
              >
                <FiGlobe className="w-4 h-4" />
                {language === 'en' ? 'العربية' : 'English'}
              </button>
              <button 
                onClick={handleFullChatClick}
                className="text-blue-500 hover:text-blue-600 font-medium text-sm"
              >
                {isFullScreen ? t.minimizeChat + ' ↙' : t.fullChat + ' ↗'}
              </button>
            </div>
          )}
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
          {messages.length === 0 && !loading && (
            <div className="text-center py-12">
              <div className="text-gray-400 text-lg mb-8">
                {t.greeting}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] px-5 py-3 rounded-2xl text-base leading-relaxed ${
                  m.role === "user"
                    ? "bg-blue-500 text-white rounded-br-md"
                    : "bg-gray-100 text-gray-800 rounded-bl-md"
                }`}
              >
                <div className="whitespace-pre-line">{m.content}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="px-5 py-3 rounded-2xl bg-gray-100 text-gray-600 animate-pulse text-base rounded-bl-md">
                {t.thinking}
              </div>
            </div>
          )}

          <div ref={endRef} />
        </div>

        {/* Suggested prompts - only show after mount */}
        {isMounted && messages.length === 0 && (
          <div className="px-8 pb-6">
            <div className="flex flex-wrap gap-3">
              {t.suggestions.map((text, idx) => (
                <button
                  key={idx}
                  className="bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 text-sm px-4 py-3 rounded-xl"
                  onClick={() => handleSuggestionClick(text)}
                >
                  {text}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input bar */}
        <div className="border-t border-gray-100 p-6 relative">
          {/* Autocomplete dropdown */}
          {isMounted && showAutocomplete && filteredSuggestions.length > 0 && (
            <div className="absolute bottom-full left-6 right-6 mb-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto z-10">
              {filteredSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleAutocompleteClick(suggestion)}
                  className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                    index === activeSuggestionIndex ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          
          <form
            onSubmit={sendMessage}
            className="flex items-center gap-3 bg-gray-50 rounded-2xl p-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              disabled={loading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => {
                if (input.trim() && input.length > 1) {
                  setShowAutocomplete(true);
                }
              }}
              onBlur={() => {
                setTimeout(() => setShowAutocomplete(false), 150);
              }}
              className="flex-1 bg-transparent text-gray-800 text-base placeholder-gray-500 focus:outline-none px-4 py-3"
              placeholder={t.placeholder}
            />
            {isMounted && (
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-gray-200 hover:bg-gray-300 text-gray-600 p-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FiSend className="w-5 h-5" />
              </button>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="px-6 pb-4">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <div className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center font-bold text-xs">
              AI
            </div>
          </div>
          <div className="text-center text-xs text-gray-400 mt-2">
            {t.footer}
          </div>
        </div>
      </div>
    </div>
  );
}