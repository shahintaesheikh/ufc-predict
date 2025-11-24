"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

export default function App() {
  const [fighter1, setFighter1] = useState("")
  const [fighter2, setFighter2] = useState("")
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<{ winner: string; confidence: number } | null>(null)

  const handlePredict = async () => {
    if (!fighter1.trim() || !fighter2.trim()) {
      alert("Please enter both fighter names")
      return
    }

    setLoading(true)

    // In a real app, this would be a fetch to your actual backend URL
    // e.g., const response = await fetch("https://your-api.com/predict", ...)
    // For this frontend demo, we'll simulate a backend response
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000)) // Simulate network delay

      // Random mock prediction logic for demonstration
      const randomWinner = Math.random() > 0.5 ? fighter1 : fighter2
      const randomConfidence = 0.5 + Math.random() * 0.4 // 50-90%

      setPrediction({
        winner: randomWinner,
        confidence: randomConfidence,
      })
    } catch (error) {
      console.error("Prediction error:", error)
      alert("Failed to get prediction.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 w-full">
      {/* Background accent */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary opacity-5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block mb-4">
            <span className="text-6xl font-black tracking-tighter">⚔️</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-balance mb-2">
            <span className="text-primary">UFC</span> <span className="text-accent">FIGHT</span>{" "}
            <span className="text-foreground">PREDICTOR</span>
          </h1>
          <p className="text-muted-foreground text-lg">Advanced ML Predictions</p>
        </div>

        {/* Main Card */}
        <Card className="bg-card border-border p-8 md:p-12 shadow-2xl">
          <div className="space-y-8">
            {/* Fighter Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Fighter 1 */}
              <div className="space-y-3">
                <label className="block text-sm font-bold text-primary uppercase tracking-wider">Fighter 1</label>
                <Input
                  placeholder="Enter fighter name"
                  value={fighter1}
                  onChange={(e) => setFighter1(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handlePredict()}
                  className="bg-input border-border placeholder-muted-foreground/50 text-foreground h-12 text-base"
                />
              </div>

              {/* Fighter 2 */}
              <div className="space-y-3">
                <label className="block text-sm font-bold text-primary uppercase tracking-wider">Fighter 2</label>
                <Input
                  placeholder="Enter fighter name"
                  value={fighter2}
                  onChange={(e) => setFighter2(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handlePredict()}
                  className="bg-input border-border placeholder-muted-foreground/50 text-foreground h-12 text-base"
                />
              </div>
            </div>

            {/* VS Divider */}
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary to-transparent"></div>
              <span className="text-primary font-black text-xl">VS</span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary to-transparent"></div>
            </div>

            {/* Predict Button */}
            <Button
              onClick={handlePredict}
              disabled={loading || !fighter1.trim() || !fighter2.trim()}
              className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-black text-lg h-14 uppercase tracking-wider rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="inline-block animate-spin">⚡</span>
                  Predicting...
                </span>
              ) : (
                "PREDICT"
              )}
            </Button>

            {/* Prediction Result */}
            {prediction && !loading && (
              <div className="mt-8 p-6 bg-gradient-to-r from-accent/10 to-primary/10 border border-accent/30 rounded-lg animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="text-center">
                  <p className="text-muted-foreground text-sm mb-2">PREDICTED WINNER</p>
                  <p className="text-3xl font-black text-primary mb-2 uppercase text-balance">{prediction.winner}</p>
                  <div className="flex items-center justify-center gap-2">
                    <div className="flex-1 bg-border rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-primary to-accent h-2 rounded-full transition-all duration-500"
                        style={{ width: `${prediction.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-accent font-bold text-lg min-w-fit">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Footer Info */}
        <p className="text-center text-muted-foreground text-sm mt-8">
          Predictions powered by advanced machine learning models
        </p>
      </div>
    </main>
  )
}

