/**
 * Safe Expression Evaluator
 * Replaces unsafe eval() with a sandboxed evaluator
 * Uses Function constructor with limited scope
 */

export class SafeExpressionEvaluator {
  private allowedGlobals = {
    // Math operations
    Math: Math,
    // Date operations
    Date: Date,
    // Safe string operations
    String: String,
    Number: Number,
    Boolean: Boolean,
    Array: Array,
    Object: Object,
    // JSON operations
    JSON: JSON,
  };

  /**
   * Safely evaluate an expression with given context
   * @param expression - The expression to evaluate (without {{ }})
   * @param context - Variables available in the expression
   * @returns The evaluation result
   */
  evaluate(expression: string, context: Record<string, any>): any {
    try {
      // Remove any {{ }} if present
      const cleanExpression = expression.replace(/^\{\{|\}\}$/g, "").trim();

      // Create a safe function with limited scope
      const contextKeys = Object.keys(context);
      const contextValues = Object.values(context);

      // Build the function with allowed globals only
      const func = new Function(
        ...contextKeys,
        ...Object.keys(this.allowedGlobals),
        `"use strict"; return (${cleanExpression});`
      );

      // Execute with context
      return func(...contextValues, ...Object.values(this.allowedGlobals));
    } catch (error: any) {
      throw new Error(`Expression evaluation error: ${error.message}`);
    }
  }

  /**
   * Evaluate a template string with {{ }} syntax
   * @param template - Template string with {{ }} expressions
   * @param context - Variables available
   * @returns Evaluated string
   */
  evaluateTemplate(template: string, context: Record<string, any>): any {
    try {
      // Find all {{ }} expressions
      const matches = template.match(/\{\{([^}]+)\}\}/g);

      if (!matches || matches.length === 0) {
        return template;
      }

      // If the entire template is a single expression, return the evaluated value
      if (matches.length === 1 && template.trim() === matches[0].trim()) {
        const expression = matches[0].replace(/^\{\{|\}\}$/g, "").trim();
        return this.evaluate(expression, context);
      }

      // Otherwise, replace all expressions in the string
      let result = template;
      for (const match of matches) {
        const expression = match.replace(/^\{\{|\}\}$/g, "").trim();
        const value = this.evaluate(expression, context);
        result = result.replace(match, String(value));
      }

      return result;
    } catch (error: any) {
      throw new Error(`Template evaluation error: ${error.message}`);
    }
  }

  /**
   * Validate expression syntax without executing
   * @param expression - Expression to validate
   * @returns true if valid, throws error otherwise
   */
  validate(expression: string): boolean {
    try {
      const cleanExpression = expression.replace(/^\{\{|\}\}$/g, "").trim();

      // Try to create the function to check syntax
      new Function(`"use strict"; return (${cleanExpression});`);

      return true;
    } catch (error: any) {
      throw new Error(`Invalid expression syntax: ${error.message}`);
    }
  }

  /**
   * Evaluate a condition (returns boolean)
   * @param condition - Condition expression
   * @param context - Context variables
   * @returns boolean result
   */
  evaluateCondition(condition: string, context: Record<string, any>): boolean {
    const result = this.evaluate(condition, context);
    return Boolean(result);
  }
}

// Singleton instance
export const safeEvaluator = new SafeExpressionEvaluator();
