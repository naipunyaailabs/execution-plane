import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

interface ActionNodeConfigProps {
  actionType: string;
  config: Record<string, any>;
  onChange: (config: Record<string, any>) => void;
}

export function ActionNodeConfig({ actionType, config, onChange }: ActionNodeConfigProps) {
  const updateConfig = (updates: Record<string, any>) => {
    onChange({ ...config, ...updates });
  };

  if (!actionType) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Please select an action type first
        </AlertDescription>
      </Alert>
    );
  }

  switch (actionType) {
    case "http_request":
    case "api_call":
      return (
        <div className="space-y-3">
          <div>
            <Label>HTTP Method</Label>
            <Select 
              value={config.method || "GET"} 
              onValueChange={(v) => updateConfig({ method: v })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="GET">GET</SelectItem>
                <SelectItem value="POST">POST</SelectItem>
                <SelectItem value="PUT">PUT</SelectItem>
                <SelectItem value="PATCH">PATCH</SelectItem>
                <SelectItem value="DELETE">DELETE</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>URL</Label>
            <Input
              placeholder="https://api.example.com/endpoint or {{ $json.url }}"
              value={config.url || ""}
              onChange={(e) => updateConfig({ url: e.target.value })}
              className="mt-1 font-mono text-sm"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Use expressions like {`{{ $json.field }}`} for dynamic values
            </p>
          </div>
          
          <div>
            <Label>Headers (JSON)</Label>
            <Textarea
              placeholder={`{\n  "Content-Type": "application/json",\n  "Authorization": "Bearer {{ $credentials.api_key }}"\n}`}
              value={config.headers ? JSON.stringify(config.headers, null, 2) : ""}
              onChange={(e) => {
                try {
                  if (e.target.value.trim()) {
                    updateConfig({ headers: JSON.parse(e.target.value) });
                  } else {
                    updateConfig({ headers: {} });
                  }
                } catch (err) {
                  // Invalid JSON, don't update
                }
              }}
              className="mt-1 font-mono text-xs"
              rows={4}
            />
          </div>
          
          {(config.method === "POST" || config.method === "PUT" || config.method === "PATCH") && (
            <div>
              <Label>Body (JSON)</Label>
              <Textarea
                placeholder={`{\n  "data": "{{ $json.value }}",\n  "timestamp": "{{ $now }}"\n}`}
                value={config.body ? JSON.stringify(config.body, null, 2) : ""}
                onChange={(e) => {
                  try {
                    if (e.target.value.trim()) {
                      updateConfig({ body: JSON.parse(e.target.value) });
                    } else {
                      updateConfig({ body: {} });
                    }
                  } catch (err) {
                    // Invalid JSON, don't update
                  }
                }}
                className="mt-1 font-mono text-xs"
                rows={5}
              />
            </div>
          )}

          <div>
            <Label>Timeout (seconds)</Label>
            <Input
              type="number"
              value={config.timeout || 30}
              onChange={(e) => updateConfig({ timeout: parseInt(e.target.value) || 30 })}
              className="mt-1"
              min="1"
              max="300"
            />
          </div>
        </div>
      );
    
    case "data_transform":
    case "transform":
      return (
        <div className="space-y-3">
          <div>
            <Label>Transform Expression</Label>
            <Textarea
              placeholder={`return {\n  fullName: $json.firstName + ' ' + $json.lastName,\n  email: $json.email.toLowerCase(),\n  timestamp: $now\n}`}
              value={config.expression || ""}
              onChange={(e) => updateConfig({ expression: e.target.value })}
              className="mt-1 font-mono text-sm"
              rows={8}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Write JavaScript to transform data. Return an object with the transformed data.
            </p>
          </div>

          <div>
            <Label>Transform Type</Label>
            <Select 
              value={config.transformType || "javascript"} 
              onValueChange={(v) => updateConfig({ transformType: v })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="javascript">JavaScript</SelectItem>
                <SelectItem value="jmespath">JMESPath</SelectItem>
                <SelectItem value="jsonata">JSONata</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      );
    
    case "webhook":
      return (
        <div className="space-y-3">
          <div>
            <Label>Webhook URL</Label>
            <Input
              placeholder="https://webhook.example.com/endpoint"
              value={config.url || ""}
              onChange={(e) => updateConfig({ url: e.target.value })}
              className="mt-1"
            />
          </div>

          <div>
            <Label>HTTP Method</Label>
            <Select 
              value={config.method || "POST"} 
              onValueChange={(v) => updateConfig({ method: v })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="POST">POST</SelectItem>
                <SelectItem value="PUT">PUT</SelectItem>
                <SelectItem value="PATCH">PATCH</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Payload Template (JSON)</Label>
            <Textarea
              placeholder={`{\n  "event": "workflow.completed",\n  "data": "{{ $json }}",\n  "workflow_id": "{{ $workflow.id }}"\n}`}
              value={config.payload ? JSON.stringify(config.payload, null, 2) : ""}
              onChange={(e) => {
                try {
                  if (e.target.value.trim()) {
                    updateConfig({ payload: JSON.parse(e.target.value) });
                  } else {
                    updateConfig({ payload: {} });
                  }
                } catch (err) {
                  // Invalid JSON
                }
              }}
              className="mt-1 font-mono text-xs"
              rows={6}
            />
          </div>
        </div>
      );
    
    case "wait":
    case "delay":
      return (
        <div className="space-y-3">
          <div>
            <Label>Wait Duration (seconds)</Label>
            <Input
              type="number"
              value={config.duration || 1}
              onChange={(e) => updateConfig({ duration: parseFloat(e.target.value) || 1 })}
              className="mt-1"
              min="0.1"
              max="3600"
              step="0.1"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Pause workflow execution for the specified duration
            </p>
          </div>

          <div>
            <Label>Wait Until (Optional)</Label>
            <Input
              type="datetime-local"
              value={config.waitUntil || ""}
              onChange={(e) => updateConfig({ waitUntil: e.target.value })}
              className="mt-1"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Alternative: Wait until a specific date/time
            </p>
          </div>
        </div>
      );
    
    case "custom":
      return (
        <div className="space-y-3">
          <div>
            <Label>Custom Script</Label>
            <Textarea
              placeholder={`// Your custom JavaScript code\nconst result = processData($json);\nreturn result;`}
              value={config.script || ""}
              onChange={(e) => updateConfig({ script: e.target.value })}
              className="mt-1 font-mono text-sm"
              rows={10}
            />
          </div>

          <div>
            <Label>Script Language</Label>
            <Select 
              value={config.language || "javascript"} 
              onValueChange={(v) => updateConfig({ language: v })}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="javascript">JavaScript</SelectItem>
                <SelectItem value="python">Python</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      );
    
    default:
      return (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No configuration available for action type: {actionType}
          </AlertDescription>
        </Alert>
      );
  }
}
