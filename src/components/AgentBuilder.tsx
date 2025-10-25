import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles, Cpu, MessageSquare, Zap, Database, GitBranch, AlertTriangle } from "lucide-react";
import { toast } from "@/hooks/use-toast";

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
];

const MODELS = {
  openai: ["gpt-4o", "gpt-4-turbo", "gpt-4o-mini"],
  anthropic: ["claude-sonnet-4-5", "claude-opus-4-1", "claude-3-5-haiku"],
  google: ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
};

const AGENT_TYPES = [
  { value: "react", label: "ReAct", description: "Reasoning and Acting pattern" },
  { value: "plan-execute", label: "Plan & Execute", description: "Planning then execution" },
  { value: "reflection", label: "Reflection", description: "Self-critique and improve" },
  { value: "custom", label: "Custom Graph", description: "Define your own flow" },
];

const MEMORY_TYPES = [
  { value: "memory-saver", label: "MemorySaver (SQLite)" },
  { value: "postgres", label: "PostgreSQL" },
  { value: "redis", label: "Redis" },
  { value: "none", label: "No Persistence" },
];

const AVAILABLE_TOOLS = [
  { id: "tavily_search", label: "Tavily Search" },
  { id: "python_repl", label: "Python REPL" },
  { id: "arxiv", label: "arXiv Papers" },
  { id: "wikipedia", label: "Wikipedia" },
  { id: "duckduckgo", label: "DuckDuckGo" },
  { id: "human_approval", label: "Human Approval" },
];

export function AgentBuilder() {
  const [agentName, setAgentName] = useState("");
  const [agentType, setAgentType] = useState("react");
  const [llmProvider, setLlmProvider] = useState("anthropic");
  const [llmModel, setLlmModel] = useState("claude-sonnet-4-5");
  const [temperature, setTemperature] = useState([0.7]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [maxIterations, setMaxIterations] = useState("15");
  const [memoryType, setMemoryType] = useState("memory-saver");
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const [humanInLoop, setHumanInLoop] = useState(false);
  const [recursionLimit, setRecursionLimit] = useState("25");
  const [timeoutSeconds, setTimeoutSeconds] = useState("120");

  const handleProviderChange = (provider: string) => {
    setLlmProvider(provider);
    setLlmModel(MODELS[provider as keyof typeof MODELS][0]);
  };

  const handleToolToggle = (toolId: string) => {
    setSelectedTools(prev =>
      prev.includes(toolId)
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    );
  };

  const handleGenerateAgent = () => {
    if (!agentName.trim()) {
      toast({
        title: "Agent name required",
        description: "Please provide a name for your agent",
        variant: "destructive",
      });
      return;
    }

    const config = {
      agentName,
      agentType,
      llmProvider,
      llmModel,
      temperature: temperature[0],
      systemPrompt,
      tools: selectedTools,
      maxIterations: parseInt(maxIterations),
      memoryType,
      streamingEnabled,
      humanInLoop,
      recursionLimit: parseInt(recursionLimit),
      timeoutSeconds: parseInt(timeoutSeconds),
    };

    console.log("Generated LangGraph Agent Configuration:", config);
    
    toast({
      title: "Agent Generated! 🎉",
      description: `${agentName} configured with ${agentType} architecture`,
    });
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-background via-background to-background/95 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_hsl(263_40%_10%)_0%,_hsl(240_10%_3.9%)_50%)] pointer-events-none" />
      
      <div className="relative z-10 container mx-auto px-4 py-6 max-w-7xl">
        {/* Compact Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 mb-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
            <Sparkles className="w-3.5 h-3.5 text-accent" />
            <span className="text-xs font-medium text-accent">LangGraph Agent Builder</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2 bg-gradient-to-r from-foreground via-accent to-primary bg-clip-text text-transparent">
            Configure Your Agent
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Main Configuration - Left Column */}
          <div className="lg:col-span-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Agent Identity & Type */}
              <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
                <div className="flex items-center gap-2 mb-3">
                  <Cpu className="w-4 h-4 text-primary" />
                  <h2 className="text-sm font-semibold">Identity & Type</h2>
                </div>
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="agent-name" className="text-xs">Agent Name</Label>
                    <Input
                      id="agent-name"
                      placeholder="ResearchAssistant"
                      value={agentName}
                      onChange={(e) => setAgentName(e.target.value)}
                      className="mt-1.5 h-9 bg-secondary/50 border-border text-sm"
                    />
                  </div>
                  <div>
                    <Label htmlFor="agent-type" className="text-xs">Architecture Pattern</Label>
                    <Select value={agentType} onValueChange={setAgentType}>
                      <SelectTrigger id="agent-type" className="mt-1.5 h-9 bg-secondary/50 border-border text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {AGENT_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            <div className="flex flex-col">
                              <span className="text-sm">{type.label}</span>
                              <span className="text-xs text-muted-foreground">{type.description}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </Card>

              {/* LLM Configuration */}
              <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  <h2 className="text-sm font-semibold">LLM Settings</h2>
                </div>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="provider" className="text-xs">Provider</Label>
                      <Select value={llmProvider} onValueChange={handleProviderChange}>
                        <SelectTrigger id="provider" className="mt-1.5 h-9 bg-secondary/50 border-border text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {LLM_PROVIDERS.map(provider => (
                            <SelectItem key={provider.value} value={provider.value}>
                              {provider.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="model" className="text-xs">Model</Label>
                      <Select value={llmModel} onValueChange={setLlmModel}>
                        <SelectTrigger id="model" className="mt-1.5 h-9 bg-secondary/50 border-border text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {MODELS[llmProvider as keyof typeof MODELS].map(model => (
                            <SelectItem key={model} value={model}>
                              {model}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="temperature" className="text-xs">Temperature: {temperature[0].toFixed(1)}</Label>
                    <Slider
                      id="temperature"
                      min={0}
                      max={2}
                      step={0.1}
                      value={temperature}
                      onValueChange={setTemperature}
                      className="mt-2"
                    />
                  </div>
                </div>
              </Card>
            </div>

            {/* System Prompt */}
            <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare className="w-4 h-4 text-primary" />
                <h2 className="text-sm font-semibold">System Prompt</h2>
              </div>
              <Textarea
                placeholder="You are a helpful AI assistant that..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="min-h-[80px] bg-secondary/50 border-border resize-none text-sm"
              />
            </Card>

            {/* Tools & Memory */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Tools Selection */}
              <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-primary" />
                  <h2 className="text-sm font-semibold">Tools</h2>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {AVAILABLE_TOOLS.map(tool => (
                    <div
                      key={tool.id}
                      className="flex items-center space-x-2 p-2 rounded border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer"
                      onClick={() => handleToolToggle(tool.id)}
                    >
                      <Checkbox
                        id={tool.id}
                        checked={selectedTools.includes(tool.id)}
                        onCheckedChange={() => handleToolToggle(tool.id)}
                      />
                      <label htmlFor={tool.id} className="text-xs font-medium cursor-pointer flex-1">
                        {tool.label}
                      </label>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Memory & State */}
              <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
                <div className="flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4 text-primary" />
                  <h2 className="text-sm font-semibold">Memory & State</h2>
                </div>
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="memory-type" className="text-xs">Checkpoint Storage</Label>
                    <Select value={memoryType} onValueChange={setMemoryType}>
                      <SelectTrigger id="memory-type" className="mt-1.5 h-9 bg-secondary/50 border-border text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MEMORY_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <Label htmlFor="human-loop" className="text-xs">Human-in-the-Loop</Label>
                    <Switch
                      id="human-loop"
                      checked={humanInLoop}
                      onCheckedChange={setHumanInLoop}
                    />
                  </div>
                </div>
              </Card>
            </div>

            {/* Execution Controls */}
            <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
              <div className="flex items-center gap-2 mb-3">
                <GitBranch className="w-4 h-4 text-primary" />
                <h2 className="text-sm font-semibold">Execution Controls</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <Label htmlFor="max-iterations" className="text-xs">Max Iterations</Label>
                  <Input
                    id="max-iterations"
                    type="number"
                    min="1"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(e.target.value)}
                    className="mt-1.5 h-9 bg-secondary/50 border-border text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="recursion-limit" className="text-xs">Recursion Limit</Label>
                  <Input
                    id="recursion-limit"
                    type="number"
                    min="1"
                    value={recursionLimit}
                    onChange={(e) => setRecursionLimit(e.target.value)}
                    className="mt-1.5 h-9 bg-secondary/50 border-border text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="timeout" className="text-xs">Timeout (sec)</Label>
                  <Input
                    id="timeout"
                    type="number"
                    min="1"
                    value={timeoutSeconds}
                    onChange={(e) => setTimeoutSeconds(e.target.value)}
                    className="mt-1.5 h-9 bg-secondary/50 border-border text-sm"
                  />
                </div>
                <div className="flex flex-col justify-between">
                  <Label htmlFor="streaming" className="text-xs mb-1">Streaming</Label>
                  <div className="flex items-center h-9">
                    <Switch
                      id="streaming"
                      checked={streamingEnabled}
                      onCheckedChange={setStreamingEnabled}
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Sidebar - Summary & Generate */}
          <div className="lg:col-span-4 space-y-4">
            {/* Configuration Summary */}
            <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
              <h3 className="text-xs font-semibold text-muted-foreground mb-3 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5" />
                Configuration Summary
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Architecture</span>
                  <span className="font-medium">{AGENT_TYPES.find(t => t.value === agentType)?.label}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Provider</span>
                  <span className="font-medium capitalize">{llmProvider}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Model</span>
                  <span className="font-medium">{llmModel}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Temperature</span>
                  <span className="font-medium">{temperature[0].toFixed(1)}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Tools</span>
                  <span className="font-medium">{selectedTools.length} enabled</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Memory</span>
                  <span className="font-medium text-xs">{MEMORY_TYPES.find(m => m.value === memoryType)?.label}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Max Iterations</span>
                  <span className="font-medium">{maxIterations}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-border/50">
                  <span className="text-muted-foreground">Human Approval</span>
                  <span className="font-medium">{humanInLoop ? "Enabled" : "Disabled"}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-muted-foreground">Streaming</span>
                  <span className="font-medium">{streamingEnabled ? "Enabled" : "Disabled"}</span>
                </div>
              </div>
            </Card>

            {/* Generate Button */}
            <Card className="p-4 bg-card/50 backdrop-blur-sm border-border">
              <Button
                variant="hero"
                size="lg"
                className="w-full"
                onClick={handleGenerateAgent}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Agent
              </Button>
              <p className="text-xs text-muted-foreground text-center mt-3">
                Click to generate your LangGraph agent with the configured settings
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
