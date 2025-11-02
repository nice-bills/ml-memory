"use client";

import { useState, FormEvent, ChangeEvent, useRef, useEffect, useCallback, useMemo } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { Button } from "@/components/ui/button";
import { ArrowUpIcon, Plus, Menu, X, History, Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

// --- Types & Constants ---
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9696";

type MessageData = {
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

type ConversationInfo = {
  id: number;
  title: string;
};

// --- Custom Components (Unchanged logic) ---
const CustomCodeBlock = ({ className, children }: { className?: string; children: React.ReactNode; }) => {
  const [isCopied, setIsCopied] = useState(false);
  const codeString = String(children).replace(/\n$/, "");
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : "text";

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };

  return (
    <div className="relative bg-zinc-900 rounded-md my-2">
      <div className="flex items-center justify-between px-4 py-1.5 border-b border-zinc-700">
        <span className="text-xs text-zinc-400">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors"
        >
          {isCopied ? (<><Check size={14} />Copied!</>) : (<><Copy size={14} />Copy code</>)}
        </button>
      </div>
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        wrapLines={true}
        customStyle={{ padding: "1rem", margin: "0", backgroundColor: "transparent", }}
      >
        {codeString}
      </SyntaxHighlighter>
    </div>
  );
};

const AiBubble = ({ content }: { content: string }) => (
  <div className="max-w-[75%] p-3 rounded-lg bg-white dark:bg-zinc-800 text-black dark:text-white shadow-md break-words">
    <ReactMarkdown
      components={{
        code: (props) => {
          const match = /language-(\w+)/.exec(props.className || "");
          return match ? (
            <CustomCodeBlock className={props.className} children={props.children} />
          ) : (
            <code className="bg-zinc-200 dark:bg-zinc-700 rounded-md px-1.5 py-0.5 text-red-500 break-words">{props.children}</code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  </div>
);

const UserBubble = ({ content }: { content: string }) => (
  <div className="max-w-[75%] p-3 rounded-lg bg-blue-600 text-white break-words">
    <ReactMarkdown>{content}</ReactMarkdown>
  </div>
);

// --- Main Component ---
export default function ChatStreaming() {
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // --- NEW STATE for Sidebar and Conversation ---
  const [conversations, setConversations] = useState<ConversationInfo[]>([]);
  const [currentConvoId, setCurrentConvoId] = useState<number | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Hardcode user ID for now
  const userId = "guest_session";

  // --- API Functions ---
  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/conversations`, {
        headers: { 'X-User-ID': userId }
      });
      if (!res.ok) throw new Error("Failed to fetch conversations");
      const data = await res.json();
      setConversations(data);
      
      // If no convo is selected, select the latest one
      if (currentConvoId === null && data.length > 0) {
        setCurrentConvoId(data[0].id);
      }
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  }, [userId, currentConvoId]);

  const fetchHistory = useCallback(async (id: number) => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/history/${id}`);
      if (!res.ok) throw new Error("Failed to fetch history");
      const data: MessageData[] = await res.json();
      setMessages(data);
    } catch (error) {
      console.error("Error fetching history:", error);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // --- Effects ---
  // 1. Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);
  
  // 2. Fetch history when currentConvoId changes
  useEffect(() => {
    if (currentConvoId !== null) {
      fetchHistory(currentConvoId);
    }
  }, [currentConvoId, fetchHistory]);
  
  // 3. Auto-scroll when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const selectConversation = (id: number) => {
    setCurrentConvoId(id);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };
  
  const createNewConversation = () => {
    setCurrentConvoId(null); // Triggers a new chat creation on next submit
    setMessages([]); // Clear the history instantly
    setIsSidebarOpen(false);
  }

  // --- Main Chat Submission ---
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const userInput = input.trim();
    if (!userInput || currentConvoId === null) return;

    setIsLoading(true);
    setInput("");

    // Add user message to UI immediately
    const userMessage: MessageData = { role: "user", content: userInput, created_at: new Date().toISOString() };
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "assistant", content: "", created_at: new Date().toISOString() }, // Placeholder
    ]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-User-ID": userId // Send the hardcoded user ID
        },
        body: JSON.stringify({ 
          user_input: userInput,
          conversation_id: currentConvoId 
        }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }
      
      // Update conversations list after submit, in case title changed
      fetchConversations(); 

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          const updatedLastMessage = {
            ...lastMessage,
            content: lastMessage.content + chunk,
          };
          return [
            ...prevMessages.slice(0, -1),
            updatedLastMessage,
          ];
        });
      }
    } catch (error) {
      console.error("Streaming error:", error);
      // Simple error message display
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "❌ Connection failed. Please check your backend server.",
          created_at: new Date().toISOString()
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Sidebar Component ---
  const Sidebar = useMemo(() => (
    <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-zinc-800 dark:bg-zinc-950 border-r border-zinc-700 transform ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"} transition-transform duration-300 ease-in-out md:relative md:translate-x-0 md:flex flex-col`}>
      
      {/* Sidebar Header */}
      <div className="flex justify-between items-center p-4 border-b border-zinc-700">
        <h2 className="text-lg font-semibold text-white flex items-center">
            <History size={20} className="mr-2 text-blue-400" />
            Chat History
        </h2>
        <button 
            onClick={() => setIsSidebarOpen(false)} 
            className="md:hidden text-white hover:text-red-400"
        >
            <X size={24} />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <Button 
            onClick={createNewConversation}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold"
        >
            <Plus size={20} className="mr-2" /> Start New Chat
        </Button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto space-y-1 p-4">
        {conversations.map((convo) => (
          <Button
            key={convo.id}
            variant="ghost"
            onClick={() => selectConversation(convo.id)}
            className={`w-full justify-start text-sm truncate p-3 ${
              convo.id === currentConvoId ? 'bg-zinc-700 text-white' : 'text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            {convo.title || "New Chat"}
            {/* We could add a delete button here: <Trash2 size={14} className="ml-auto" /> */}
          </Button>
        ))}
        {conversations.length === 0 && !isLoading && (
            <p className="text-zinc-500 text-sm italic">No history found.</p>
        )}
      </div>
    </div>
  ), [conversations, currentConvoId, isSidebarOpen]);
  
  // --- Main Render ---
  return (
    <div className="flex min-h-screen bg-zinc-100 dark:bg-zinc-900">
      
      {/* 1. Sidebar */}
      {Sidebar}

      {/* 2. Main Chat Area */}
      <div className="flex flex-col flex-1 h-screen relative">
          
          {/* Top Header/Toggle */}
          <header className="sticky top-0 z-10 p-4 border-b bg-zinc-100 dark:bg-zinc-900 md:hidden">
              <Button onClick={() => setIsSidebarOpen(true)} variant="ghost" size="icon">
                  <Menu size={24} className="text-white" />
              </Button>
              <span className="ml-4 text-white font-semibold">
                {conversations.find(c => c.id === currentConvoId)?.title || "New Chat"}
              </span>
          </header>

          {/* Chat Content Area (Scrollable) */}
          <div className="flex-1 overflow-y-auto" style={{ scrollbarGutter: 'stable' }}>
              <div className="w-full max-w-3xl mx-auto space-y-4 py-8 px-4">
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${
                        msg.role === "user" ? "justify-end" : "justify-start"
                      }`}
                    >
                      {msg.role === "user" ? (
                        <UserBubble content={msg.content} />
                      ) : (
                        <AiBubble content={msg.content} />
                      )}
                    </div>
                  ))}
                  {isLoading && (
                     <div className="flex justify-start">
                        <AiBubble content="Thinking..." />
                     </div>
                  )}
                  <div ref={messagesEndRef} />
              </div>
          </div>

          {/* Sticky Input Bar at the very bottom */}
          <div className="sticky bottom-0 w-full bg-zinc-100 dark:bg-zinc-900 border-t border-zinc-700">
              <div className="max-w-3xl mx-auto p-4">
                  <form onSubmit={handleSubmit} className="flex items-start gap-2">
                      <TextareaAutosize
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={isLoading ? "Please wait for the response..." : "Ask about applied ML..."}
                        className="flex-1 resize-none bg-white dark:bg-black shadow-md rounded-lg p-3 disabled:opacity-60"
                        disabled={isLoading || currentConvoId === null}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit(e as any);
                          }
                        }}
                        minRows={1}
                        maxRows={6}
                      />
                      <Button
                          type="submit"
                          disabled={isLoading || !input.trim() || currentConvoId === null}
                          className="rounded-lg h-12 bg-blue-600 hover:bg-blue-700"
                      >
                          <ArrowUpIcon className="h-5 w-5" />
                      </Button>
                  </form>
              </div>
          </div>
      </div>
    </div>
  );
}






// "use client";

// import { useState, FormEvent, ChangeEvent, useRef, useEffect } from "react";
// import TextareaAutosize from "react-textarea-autosize";
// import { Button } from "@/components/ui/button";
// // --- 1. IMPORT NEW ICONS ---
// import { ArrowUpIcon, Copy, Check } from "lucide-react";
// import ReactMarkdown from "react-markdown";
// import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
// import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

// type ChatMessage = {
//   role: "user" | "assistant";
//   content: string;
// };

// // --- 2. NEW COMPONENT: CustomCodeBlock ---
// // This new component will wrap our code blocks and add a copy button.
// const CustomCodeBlock = ({
//   className,
//   children,
// }: {
//   className?: string;
//   children: React.ReactNode;
// }) => {
//   const [isCopied, setIsCopied] = useState(false);
//   const codeString = String(children).replace(/\n$/, ""); // The code to copy

//   // Get the language (e.g., 'python')
//   const match = /language-(\w+)/.exec(className || "");
//   const language = match ? match[1] : "text";

//   const handleCopy = () => {
//     navigator.clipboard.writeText(codeString).then(() => {
//       setIsCopied(true);
//       setTimeout(() => setIsCopied(false), 2000); // Reset after 2 seconds
//     });
//   };

//   return (
//     // This is the dark container for the code
//     <div className="relative bg-zinc-900 rounded-md my-2">
//       {/* This is the top bar with language name and copy button */}
//       <div className="flex items-center justify-between px-4 py-1.5 border-b border-zinc-700">
//         <span className="text-xs text-zinc-400">{language}</span>
//         <button
//           onClick={handleCopy}
//           className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors"
//         >
//           {isCopied ? (
//             <>
//               <Check size={14} />
//               Copied!
//             </>
//           ) : (
//             <>
//               <Copy size={14} />
//               Copy code
//             </>
//           )}
//         </button>
//       </div>
      
//       {/* This is the syntax highlighter */}
//       <SyntaxHighlighter
//         style={vscDarkPlus}
//         language={language}
//         PreTag="div"
//         wrapLines={true}
//         // Override default styles to fit our container
//         customStyle={{
//           padding: "1rem",
//           margin: "0",
//           backgroundColor: "transparent",
//         }}
//       >
//         {codeString}
//       </SyntaxHighlighter>
//     </div>
//   );
// };

// // --- 3. UPDATED AiBubble ---
// // It now uses our new CustomCodeBlock
// const AiBubble = ({ content }: { content: string }) => {
//   return (
//     <div className="max-w-[75%] p-3 rounded-lg bg-white dark:bg-zinc-800 text-black dark:text-white shadow-md break-words">
//       <ReactMarkdown
//         components={{
//           code({ node, className, children, ...props }) {
//             const match = /language-(\w+)/.exec(className || "");
//             return match ? (
//               // Use our new custom component for full code blocks
//               <CustomCodeBlock className={className} {...props}>
//                 {children}
//               </CustomCodeBlock>
//             ) : (
//               // Keep the old style for inline `code`
//               <code
//                 className="bg-zinc-200 dark:bg-zinc-700 rounded-md px-1.5 py-0.5 text-red-500 break-words"
//                 {...props}
//               >
//                 {children}
//               </code>
//             );
//           },
//         }}
//       >
//         {content}
//       </ReactMarkdown>
//     </div>
//   );
// };

// // --- User Chat Bubble (unchanged) ---
// const UserBubble = ({ content }: { content: string }) => {
//   return (
//     <div className="max-w-[75%] p-3 rounded-lg bg-blue-600 text-white break-words">
//       <ReactMarkdown>{content}</ReactMarkdown>
//     </div>
//   );
// };

// // --- Main Chat Component (unchanged) ---
// export default function ChatStreaming() {
//   const [messages, setMessages] = useState<ChatMessage[]>([]);
//   const [input, setInput] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const messagesEndRef = useRef<HTMLDivElement>(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const handleSubmit = async (e: FormEvent) => {
//     e.preventDefault();
//     const userInput = input.trim();
//     if (!userInput) return;

//     setIsLoading(true);
//     setInput("");

//     const userMessage: ChatMessage = { role: "user", content: userInput };
//     setMessages((prev) => [
//       ...prev,
//       userMessage,
//       { role: "assistant", content: "" },
//     ]);

//     try {
//       // Using port 9696
//       const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ user_input: userInput }),
//       });

//       if (!response.body) {
//         throw new Error("Response body is null");
//       }

//       const reader = response.body.getReader();
//       const decoder = new TextDecoder();

//       while (true) {
//         const { done, value } = await reader.read();
//         if (done) break;

//         const chunk = decoder.decode(value);
//         setMessages((prevMessages) => {
//           const lastMessage = prevMessages[prevMessages.length - 1];
//           const updatedLastMessage = {
//             ...lastMessage,
//             content: lastMessage.content + chunk,
//           };
//           return [
//             ...prevMessages.slice(0, -1),
//             updatedLastMessage,
//           ];
//         });
//       }
//     } catch (error) {
//       console.error("Streaming error:", error);
//       setMessages((prev) => [
//         ...prev.slice(0, -1),
//         {
//           role: "assistant",
//           content: "Sorry, I had trouble streaming the response.",
//         },
//       ]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="flex flex-col h-screen">
//       <div className="flex-1 overflow-y-auto">
//         <div className="w-full max-w-3xl mx-auto space-y-4 py-8 px-4">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`flex ${
//                 msg.role === "user" ? "justify-end" : "justify-start"
//               }`}
//             >
//               {msg.role === "user" ? (
//                 <UserBubble content={msg.content} />
//               ) : (
//                 <AiBubble content={msg.content} />
//               )}
//             </div>
//           ))}
//           <div ref={messagesEndRef} />
//         </div>
//       </div>

//       <div className="sticky bottom-0 w-full bg-zinc-100 dark:bg-zinc-900">
//         <div className="max-w-3xl mx-auto p-4">
//           <form onSubmit={handleSubmit} className="flex items-start gap-2">
//             <TextareaAutosize
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               placeholder="Ask about applied ML..."
//               className="flex-1 resize-none bg-white dark:bg-black shadow-md rounded-lg p-3"
//               disabled={isLoading}
//               onKeyDown={(e) => {
//                 if (e.key === "Enter" && !e.shiftKey) {
//                   e.preventDefault();
//                   handleSubmit(e as any);
//                 }
//               }}
//               minRows={1}
//               maxRows={6}
//             />
//             <Button
//               type="submit"
//               disabled={isLoading || !input.trim()}
//               className="rounded-lg h-12"
//             >
//               <ArrowUpIcon className="h-5 w-5" />
//             </Button>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// }