/**
 * UFC Predictor API Service
 * Handles all communication with the backend prediction API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export interface PredictionRequest {
  red_fighter: string
  blue_fighter: string
}

export interface PredictionResponse {
  winner: string
  red_fighter: string
  blue_fighter: string
  red_win_probability: number
  blue_win_probability: number
  confidence: number
}

/**
 * Get list of all available fighters
 */
export async function getFighters(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/fighters`)
    if (!response.ok) {
      throw new Error(`Failed to fetch fighters: ${response.statusText}`)
    }
    const data = await response.json()
    return data.fighters || []
  } catch (error) {
    console.error("Error fetching fighters:", error)
    throw error
  }
}

/**
 * Get prediction for two fighters
 */
export async function predictFight(
  red_fighter: string,
  blue_fighter: string
): Promise<PredictionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        red_fighter,
        blue_fighter,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(
        errorData.detail || `Failed to get prediction: ${response.statusText}`
      )
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error("Error getting prediction:", error)
    throw error
  }
}

/**
 * Health check - verify backend is running
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error("Health check error:", error)
    throw error
  }
}
