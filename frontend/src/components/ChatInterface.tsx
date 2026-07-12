import { useState, useRef, useEffect } from 'react';
import { Send, FileUp, Paperclip, Bot, Loader2, ListTree } from 'lucide-react';
import { sendMessage, uploadFiles, type ChatResponse } from '../services/api';
import clsx from 'clsx';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    files?: File[];
    trace?: ChatResponse['trace'];
    isGenerating?: boolean;
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!inputValue.trim() && selectedFiles.length === 0) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            files: [...selectedFiles]
        };
        
        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setSelectedFiles([]);

        const assistantMsgId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, {
            id: assistantMsgId,
            role: 'assistant',
            content: '',
            isGenerating: true
        }]);

        try {
            let urls: string[] = [];
            if (userMsg.files && userMsg.files.length > 0) {
                setIsUploading(true);
                urls = await uploadFiles(userMsg.files);
                setIsUploading(false);
            }

            const response = await sendMessage(userMsg.content, urls.length > 0 ? urls : undefined);
            
            setMessages(prev => prev.map(m => m.id === assistantMsgId ? {
                ...m,
                content: response.response,
                trace: response.trace,
                isGenerating: false
            } : m));

        } catch (error: any) {
            setMessages(prev => prev.map(m => m.id === assistantMsgId ? {
                ...m,
                content: "Error: Could not process request. " + error.message,
                isGenerating: false
            } : m));
            setIsUploading(false);
        }
    };

    return (
        <div className="flex h-screen bg-white dark:bg-dark-900 transition-colors duration-300">
            {/* Sidebar for Trace */}
            <div className="w-80 border-r border-slate-200 dark:border-dark-700 bg-slate-50 dark:bg-dark-800 p-4 overflow-y-auto hidden md:block">
                <div className="flex items-center gap-2 mb-6 text-brand-500 font-semibold text-lg">
                    <ListTree /> Plan Trace
                </div>
                {messages.map(m => m.trace && (
                    <div key={m.id + '-trace'} className="mb-6 bg-white dark:bg-dark-700 p-4 rounded-xl shadow-sm border border-slate-100 dark:border-dark-600">
                        <div className="text-sm font-medium mb-2 text-slate-800 dark:text-slate-200">
                            Planner Reasoning
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">{m.trace.plan.reasoning}</p>
                        
                        <div className="space-y-2">
                            {m.trace.plan.tool_plan.map((tool, idx) => {
                                const execResult = m.trace?.executed_tools.find(t => t.tool_name === tool);
                                return (
                                    <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-50 dark:bg-dark-800 border border-slate-100 dark:border-dark-600 text-xs">
                                        <span className="font-mono text-slate-600 dark:text-slate-300">{tool}</span>
                                        {execResult ? (
                                            <span className={clsx(
                                                "px-2 py-1 rounded text-[10px] uppercase font-bold tracking-wider",
                                                execResult.status === 'success' ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                            )}>
                                                {execResult.latency_ms.toFixed(0)}ms
                                            </span>
                                        ) : (
                                            <span className="text-slate-400">Pending</span>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                ))}
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col relative">
                <header className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-dark-700 bg-white/80 dark:bg-dark-900/80 backdrop-blur-sm sticky top-0 z-10">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-brand-500 to-blue-500 bg-clip-text text-transparent flex items-center gap-2">
                        <Bot className="text-brand-500" />
                        OmniAgent
                    </h1>
                </header>

                <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <Bot size={64} className="mb-4 text-slate-200 dark:text-dark-700" />
                            <p className="text-lg font-medium text-slate-500">I can analyze PDFs, images, and audio.</p>
                            <p className="text-sm">Upload a file or type a message to start.</p>
                        </div>
                    )}
                    
                    {messages.map(msg => (
                        <div key={msg.id} className={clsx("flex gap-4 max-w-4xl mx-auto", msg.role === 'user' ? "justify-end" : "justify-start")}>
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center shrink-0">
                                    <Bot size={18} className="text-white" />
                                </div>
                            )}
                            
                            <div className={clsx(
                                "rounded-2xl px-5 py-3.5 shadow-sm max-w-[85%]",
                                msg.role === 'user' 
                                    ? "bg-brand-500 text-white" 
                                    : "bg-white dark:bg-dark-800 border border-slate-100 dark:border-dark-700 text-slate-800 dark:text-slate-100"
                            )}>
                                {msg.files && msg.files.length > 0 && (
                                    <div className="flex gap-2 flex-wrap mb-2">
                                        {msg.files.map((f, i) => (
                                            <span key={i} className="flex items-center gap-1 text-xs bg-black/10 px-2 py-1 rounded">
                                                <FileUp size={12} /> {f.name}
                                            </span>
                                        ))}
                                    </div>
                                )}
                                
                                {msg.isGenerating ? (
                                    <div className="flex items-center gap-2 text-slate-400">
                                        <Loader2 className="animate-spin" size={16} />
                                        <span>Thinking & Planning...</span>
                                    </div>
                                ) : (
                                    <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap text-sm leading-relaxed">
                                        {msg.content}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 md:p-6 bg-white dark:bg-dark-900 border-t border-slate-200 dark:border-dark-700">
                    <div className="max-w-4xl mx-auto flex items-end gap-2 relative">
                        {selectedFiles.length > 0 && (
                            <div className="absolute bottom-full left-0 mb-2 flex gap-2 w-full overflow-x-auto pb-2">
                                {selectedFiles.map((f, i) => (
                                    <div key={i} className="bg-slate-100 dark:bg-dark-800 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 border border-slate-200 dark:border-dark-700">
                                        <FileUp size={14} className="text-brand-500" />
                                        <span className="truncate max-w-[150px] dark:text-slate-300">{f.name}</span>
                                        <button onClick={() => setSelectedFiles(prev => prev.filter((_, idx) => idx !== i))} className="text-red-400 hover:text-red-600 ml-1">×</button>
                                    </div>
                                ))}
                            </div>
                        )}
                        <label className="p-3.5 rounded-xl bg-slate-100 dark:bg-dark-800 text-slate-500 hover:text-brand-500 cursor-pointer transition-colors border border-slate-200 dark:border-dark-700 shrink-0">
                            <Paperclip size={20} />
                            <input 
                                type="file" 
                                className="hidden" 
                                multiple 
                                onChange={(e) => setSelectedFiles(prev => [...prev, ...Array.from(e.target.files || [])])}
                            />
                        </label>
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder={isUploading ? "Uploading files..." : "Ask OmniAgent anything..."}
                            className="flex-1 max-h-32 min-h-[52px] bg-slate-100 dark:bg-dark-800 border border-slate-200 dark:border-dark-700 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-brand-500/50 resize-none dark:text-slate-100 placeholder-slate-400"
                            disabled={isUploading}
                        />
                        <button 
                            onClick={handleSend}
                            disabled={(!inputValue.trim() && selectedFiles.length === 0) || isUploading}
                            className="p-3.5 rounded-xl bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0 shadow-md shadow-brand-500/20"
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
