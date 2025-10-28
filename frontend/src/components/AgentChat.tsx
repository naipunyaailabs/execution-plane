import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface Agent {
  id: number;
  agent_id: string;
  name: string;
  agent_type: string;
  llm_model: string;
}

export function AgentChat() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/agents');
      if (response.ok) {
        const data = await response.json();
        setAgents(data);
        if (data.length > 0 && !selectedAgentId) {
          setSelectedAgentId(data[0].agent_id);
        }
      }
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive",
      });
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !selectedAgentId) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // TODO: Replace with actual agent chat endpoint
      const response = await fetch(`http://localhost:8000/api/v1/agents/${selectedAgentId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          role: "assistant",
          content: data.response || "Response received",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Error",
        description: "Failed to send message. Make sure the backend is running.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const selectedAgent = agents.find((a) => a.agent_id === selectedAgentId);

  return (
    <div className="min-h-screen w-full bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex flex-col gap-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Agent Chat</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Interact with your configured agents
            </p>
          </div>

          {/* Agent Selection */}
          <Card className="p-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="text-xs text-muted-foreground mb-2 block">
                  Select Agent
                </label>
                <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                  <SelectTrigger className="h-10 bg-background">
                    <SelectValue placeholder="Choose an agent" />
                  </SelectTrigger>
                  <SelectContent>
                    {agents.length === 0 ? (
                      <SelectItem value="none" disabled>
                        No agents available
                      </SelectItem>
                    ) : (
                      agents.map((agent) => (
                        <SelectItem key={agent.agent_id} value={agent.agent_id}>
                          {agent.name} ({agent.agent_type})
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
              {selectedAgent && (
                <div className="text-xs text-muted-foreground pt-6">
                  Model: {selectedAgent.llm_model}
                </div>
              )}
            </div>
          </Card>

          {/* Chat Interface */}
          <Card className="flex flex-col h-[600px]">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4" ref={scrollRef}>
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Bot className="w-12 h-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    {selectedAgentId
                      ? "Start a conversation with your agent"
                      : "Select an agent to begin"}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-3 ${
                        message.role === "user" ? "justify-end" : "justify-start"
                      }`}
                    >
                      {message.role === "assistant" && (
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-primary-foreground" />
                        </div>
                      )}
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 ${
                          message.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted text-foreground"
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                      {message.role === "user" && (
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                          <User className="w-4 h-4 text-secondary-foreground" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-primary-foreground" />
                      </div>
                      <div className="bg-muted rounded-lg px-4 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            {/* Input */}
            <div className="border-t border-border p-4">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    selectedAgentId
                      ? "Type your message..."
                      : "Select an agent first"
                  }
                  disabled={!selectedAgentId || isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={!selectedAgentId || !input.trim() || isLoading}
                  size="icon"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
