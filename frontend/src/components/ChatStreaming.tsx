"use client";

import { useState, FormEvent, ChangeEvent, useRef, useEffect } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { Button } from "@/components/ui/button";
// --- 1. IMPORT NEW ICONS ---
import { ArrowUpIcon, Copy, Check } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

// --- 2. NEW COMPONENT: CustomCodeBlock ---
// This new component will wrap our code blocks and add a copy button.
const CustomCodeBlock = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  const [isCopied, setIsCopied] = useState(false);
  const codeString = String(children).replace(/\n$/, ""); // The code to copy

  // Get the language (e.g., 'python')
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : "text";

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000); // Reset after 2 seconds
    });
  };

  return (
    // This is the dark container for the code
    <div className="relative bg-zinc-900 rounded-md my-2">
      {/* This is the top bar with language name and copy button */}
      <div className="flex items-center justify-between px-4 py-1.5 border-b border-zinc-700">
        <span className="text-xs text-zinc-400">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors"
        >
          {isCopied ? (
            <>
              <Check size={14} />
              Copied!
            </>
          ) : (
            <>
              <Copy size={14} />
              Copy code
            </>
          )}
        </button>
      </div>
      
      {/* This is the syntax highlighter */}
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        wrapLines={true}
        // Override default styles to fit our container
        customStyle={{
          padding: "1rem",
          margin: "0",
          backgroundColor: "transparent",
        }}
      >
        {codeString}
      </SyntaxHighlighter>
    </div>
  );
};

// --- 3. UPDATED AiBubble ---
// It now uses our new CustomCodeBlock
const AiBubble = ({ content }: { content: string }) => {
  return (
    <div className="max-w-[75%] p-3 rounded-lg bg-white dark:bg-zinc-800 text-black dark:text-white shadow-md break-words">
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return match ? (
              // Use our new custom component for full code blocks
              <CustomCodeBlock className={className} {...props}>
                {children}
              </CustomCodeBlock>
            ) : (
              // Keep the old style for inline `code`
              <code
                className="bg-zinc-200 dark:bg-zinc-700 rounded-md px-1.5 py-0.5 text-red-500 break-words"
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

// --- User Chat Bubble (unchanged) ---
const UserBubble = ({ content }: { content: string }) => {
  return (
    <div className="max-w-[75%] p-3 rounded-lg bg-blue-600 text-white break-words">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

// --- Main Chat Component (unchanged) ---
export default function ChatStreaming() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const userInput = input.trim();
    if (!userInput) return;

    setIsLoading(true);
    setInput("");

    const userMessage: ChatMessage = { role: "user", content: userInput };
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "assistant", content: "" },
    ]);

    try {
      // Using port 9696
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

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
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "Sorry, I had trouble streaming the response.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto">
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
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="sticky bottom-0 w-full bg-zinc-100 dark:bg-zinc-900">
        <div className="max-w-3xl mx-auto p-4">
          <form onSubmit={handleSubmit} className="flex items-start gap-2">
            <TextareaAutosize
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about applied ML..."
              className="flex-1 resize-none bg-white dark:bg-black shadow-md rounded-lg p-3"
              disabled={isLoading}
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
              disabled={isLoading || !input.trim()}
              className="rounded-lg h-12"
            >
              <ArrowUpIcon className="h-5 w-5" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}