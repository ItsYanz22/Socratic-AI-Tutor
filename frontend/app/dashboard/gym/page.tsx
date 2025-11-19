'use client'

import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

// --- NEW IMPORTS ---
import { useAuth } from "@/app/context/AuthContext"
import { useState, useEffect } from 'react'
import { useRouter } from "next/navigation"
import Editor from "@monaco-editor/react" // The code editor

// Define the shape of a chat message
interface Message {
  role: 'user' | 'ai'
  content: string
}

export default function GymPage() {
  // --- 1. SET UP STATE ---
  const { session, accessToken } = useAuth() // Get our login token
  const router = useRouter()

  // State for the AI chat
  const [prompt, setPrompt] = useState("") // What the user is typing
  const [messages, setMessages] = useState<Message[]>([ // The chat history
    {
      role: 'ai',
      content: "Hi! I'm Sahayogi. I'm here to help you solve this sandbox. What's your first question?"
    }
  ])

  // State for the code editor
  const [code, setCode] = useState<string>("# Write your Python script here\nprint('Hello, Sahayogi!')")

  // --- 2. PROTECT THE ROUTE ---
  useEffect(() => {
    if (session === null) {
      router.push('/login')
    }
  }, [session, router])

  // --- 3. HANDLE CHAT SEND ---
  const handleSend = async () => {
    if (!prompt.trim() || !accessToken) return // Don't send empty messages

    // Add user's message to chat
    const newUserMessage: Message = { role: 'user', content: prompt }
    const newMessages = [...messages, newUserMessage]
    setMessages(newMessages)
    setPrompt("") // Clear the input

    // Get the API URL from our environment
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    try {
      // Send the prompt and history to the backend
      const response = await fetch(`${apiUrl}/api/v1/tutor/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}` // <-- This is the KEY
        },
        body: JSON.stringify({
          prompt: prompt,
          chat_history: newMessages.slice(0, -1) // Send all *but* the new prompt
        })
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      const data = await response.json()

      // Add AI's response to chat
      setMessages([
        ...newMessages,
        { role: 'ai', content: data.response }
      ])

    } catch (error) {
      console.error("Error connecting to AI model:", error)
      setMessages([
        ...newMessages,
        { role: 'ai', content: "Sorry, I'm having trouble connecting to my brain. Please try again." }
      ])
    }
  }

  // TODO: Add a handleSumbitCode function

  if (!session) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  // --- 4. RENDER THE FINAL UI ---
  return (
    <ResizablePanelGroup direction="horizontal" className="min-h-screen">

      {/* Panel 1: The Sandbox Challenge */}
      <ResizablePanel defaultSize={25}>
        <div className="p-6 h-full">
          <ScrollArea className="h-full">
            <h2 className="text-2xl font-bold">MeitY Cybersecurity Sandbox</h2>
            <p className="mt-4 text-sm text-muted-foreground">
              A digital twin of a power grid's control system is under attack.
              We've captured some suspicious network traffic in a file named `capture.pcap`.
              Your mission is to write a Python script to analyze this file and find the
              anomalous packet.
            </p>
            <p className="mt-4 text-sm text-muted-foreground">
              Use the Socratic Tutor on the right if you get stuck.
            </p>
          </ScrollArea>
        </div>
      </ResizablePanel>

      <ResizableHandle withHandle />

      {/* Panel 2: The Code Editor */}
      <ResizablePanel defaultSize={45}>
        <div className="flex flex-col h-full">
          <div className="p-2 border-b">
            <span className="text-sm font-medium">main.py</span>
          </div>

          <Editor
            height="100%"
            language="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || "")}
          />

          <div className="p-2 border-t">
            <Button>Submit Code</Button>
          </div>
        </div>
      </ResizablePanel>

      <ResizableHandle withHandle />

      {/* Panel 3: The Socratic Tutor Chat */}
      <ResizablePanel defaultSize={30}>
        <div className="flex flex-col h-full">
          <div className="p-3 border-b">
            <h2 className="text-lg font-semibold">Socratic AI Tutor</h2>
          </div>

          <ScrollArea className="flex-grow p-4 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg ${
                  msg.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
              </div>
            ))}
          </ScrollArea>

          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <Input
                placeholder="Ask a question..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              />
              <Button onClick={handleSend}>Send</Button>
            </div>
          </div>
        </div>
      </ResizablePanel>

    </ResizablePanelGroup>
  )
}