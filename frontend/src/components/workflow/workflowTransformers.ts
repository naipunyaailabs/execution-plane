/**
 * Workflow transformation utilities
 * Handles conversion between frontend node data and backend step definitions
 */

import { Node } from "reactflow";

/**
 * Transform node type from frontend format to backend format
 * Frontend: startNode, agentNode, etc.
 * Backend: start, agent, etc.
 */
export function transformNodeType(frontendType: string): string {
  if (!frontendType) return "agent";
  
  // Remove "Node" suffix and convert to lowercase
  return frontendType.replace(/Node$/i, "").toLowerCase();
}

/**
 * Transform parameters object to input_mapping format
 * Frontend parameters: { key: "value or {{ expression }}" }
 * Backend input_mapping: { key: "context.path.to.value" }
 */
export function transformParametersToInputMapping(
  parameters: Record<string, string> | undefined
): Record<string, string> | undefined {
  if (!parameters || Object.keys(parameters).length === 0) {
    return undefined;
  }

  const inputMapping: Record<string, string> = {};
  
  for (const [key, value] of Object.entries(parameters)) {
    if (typeof value === "string") {
      // Keep expressions as-is for backend to evaluate
      inputMapping[key] = value;
    } else {
      // Convert non-string values to strings
      inputMapping[key] = String(value);
    }
  }
  
  return inputMapping;
}

/**
 * Transform a single node to backend step format with proper field mapping
 */
export function transformNodeToStep(node: Node): Record<string, any> {
  const baseStep = {
    id: node.id,
    type: transformNodeType(node.type || "agent"),
    name: node.data.label || "Unnamed Step",
    description: node.data.description || "",
    position: node.position,
    data: node.data, // Keep original data for reference
  };

  // Add type-specific configurations
  switch (node.type) {
    case "startNode":
      return {
        ...baseStep,
        // Start nodes can have input schema
        input_schema: node.data.input_schema,
      };
    
    case "endNode":
      return {
        ...baseStep,
        // End nodes can have output schema
        output_schema: node.data.output_schema,
      };
    
    case "agentNode":
      return {
        ...baseStep,
        agent_id: node.data.agent_id || "",
        input_mapping: transformParametersToInputMapping(node.data.parameters),
        retry_policy: node.data.retry_policy,
        credential_id: node.data.credential_id,
      };
    
    case "actionNode":
      return {
        ...baseStep,
        action_type: node.data.action_type || "custom",
        action_config: node.data.action_config || {},
        input_mapping: transformParametersToInputMapping(node.data.parameters),
        retry_policy: node.data.retry_policy,
        credential_id: node.data.credential_id,
      };
    
    case "loopNode":
      return {
        ...baseStep,
        loop_config: {
          collection: node.data.collection_path || node.data.collection || "",
          max_iterations: node.data.iterations || 10,
          item_variable: node.data.item_variable || "item",
        },
      };
    
    case "conditionNode":
      return {
        ...baseStep,
        condition: {
          expression: node.data.condition || "",
          type: node.data.condition_type || "javascript",
        },
      };
    
    case "errorHandlerNode":
      return {
        ...baseStep,
        error_type: node.data.error_type || "all",
        recovery_action: node.data.recovery_action || "continue",
        fallback_value: node.data.fallback_value,
      };
    
    case "chatNode":
      return {
        ...baseStep,
        welcome_message: node.data.welcomeMessage || "Hello! How can I help you?",
        wait_for_input: true,
      };
    
    case "displayNode":
      return {
        ...baseStep,
        display_format: node.data.displayFormat || "json",
        auto_refresh: node.data.autoRefresh !== false,
      };
    
    default:
      return baseStep;
  }
}

/**
 * Transform all nodes to steps with proper backend format
 */
export function transformNodesToSteps(nodes: Node[]): any[] {
  return nodes.map(transformNodeToStep);
}

/**
 * Build dependencies map from edges
 */
export function buildDependenciesFromEdges(edges: any[]): Record<string, string[]> {
  const dependencies: Record<string, string[]> = {};
  
  edges.forEach((edge) => {
    if (!dependencies[edge.target]) {
      dependencies[edge.target] = [];
    }
    
    // Store source and handle ID if it exists (for conditional branches)
    const sourceRef = edge.sourceHandle 
      ? `${edge.source}:${edge.sourceHandle}` 
      : edge.source;
    
    dependencies[edge.target].push(sourceRef);
  });
  
  return dependencies;
}

/**
 * Build conditions map from conditional edges
 */
export function buildConditionsFromEdges(
  edges: any[],
  nodes: Node[]
): Record<string, any> {
  const conditions: Record<string, any> = {};
  
  // Find condition nodes
  const conditionNodes = nodes.filter(node => node.type === "conditionNode");
  
  conditionNodes.forEach(condNode => {
    // Find edges from this condition node
    const outgoingEdges = edges.filter(edge => edge.source === condNode.id);
    
    const trueEdge = outgoingEdges.find(e => e.sourceHandle === "true");
    const falseEdge = outgoingEdges.find(e => e.sourceHandle === "false");
    
    if (trueEdge || falseEdge) {
      conditions[condNode.id] = {
        true_branch: trueEdge?.target || "END",
        false_branch: falseEdge?.target || "END",
      };
    }
  });
  
  return conditions;
}

/**
 * Complete workflow transformation from React Flow format to backend format
 */
export function transformWorkflowForBackend(
  nodes: Node[],
  edges: any[],
  workflowName: string,
  workflowDescription: string,
  triggers?: any[]
) {
  const steps = transformNodesToSteps(nodes);
  const dependencies = buildDependenciesFromEdges(edges);
  const conditions = buildConditionsFromEdges(edges, nodes);
  
  return {
    name: workflowName,
    description: workflowDescription,
    definition: {
      steps,
      dependencies,
      conditions,
    },
    triggers: triggers || [],
  };
}

/**
 * Validate workflow structure
 */
export function validateWorkflow(nodes: Node[], edges: any[]): { valid: boolean; error?: string } {
  if (nodes.length === 0) {
    return { valid: false, error: "Workflow must have at least one node" };
  }

  // Check for start node
  const hasStartNode = nodes.some(node => node.type === "startNode");
  if (!hasStartNode) {
    return { valid: false, error: "Workflow must have a Start node" };
  }

  // Check for end node
  const hasEndNode = nodes.some(node => node.type === "endNode");
  if (!hasEndNode) {
    return { valid: false, error: "Workflow must have an End node" };
  }

  // Check agent nodes have agent_id
  const agentNodes = nodes.filter(node => node.type === "agentNode");
  const invalidAgentNodes = agentNodes.filter(node => !node.data.agent_id);
  if (invalidAgentNodes.length > 0) {
    return { 
      valid: false, 
      error: `Agent nodes must have an agent selected: ${invalidAgentNodes.map(n => n.data.label).join(", ")}` 
    };
  }

  // Check action nodes have action_type
  const actionNodes = nodes.filter(node => node.type === "actionNode");
  const invalidActionNodes = actionNodes.filter(node => !node.data.action_type);
  if (invalidActionNodes.length > 0) {
    return { 
      valid: false, 
      error: `Action nodes must have an action type: ${invalidActionNodes.map(n => n.data.label).join(", ")}` 
    };
  }

  // Check all nodes (except start) have incoming edges
  const nodesExceptStart = nodes.filter(node => node.type !== "startNode");
  const nodesWithoutInput = nodesExceptStart.filter(node => 
    !edges.some(edge => edge.target === node.id)
  );
  if (nodesWithoutInput.length > 0) {
    return { 
      valid: false, 
      error: `Some nodes are not connected: ${nodesWithoutInput.map(n => n.data.label).join(", ")}` 
    };
  }

  return { valid: true };
}
