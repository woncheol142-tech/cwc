package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type TradingCommand struct {
	AccountType string   `json:"accountType"`
	Universe    []string `json:"universe"`
}

type TradeLog struct {
	ID          int64          `json:"id"`
	Timestamp   string         `json:"timestamp"`
	Symbol      string         `json:"symbol"`
	Side        string         `json:"side"`
	Quantity    int            `json:"quantity"`
	Price       float64        `json:"price"`
	Indicators  map[string]any `json:"indicators"`
	Reasoning   string         `json:"reasoning"`
	AccountType string         `json:"accountType"`
}

func main() {
	pythonBaseURL := os.Getenv("PYTHON_ENGINE_URL")
	if pythonBaseURL == "" {
		pythonBaseURL = "http://localhost:8000"
	}

	router := gin.Default()
	router.Use(cors.New(cors.Config{
		AllowOrigins: []string{"http://localhost:5173"},
		AllowMethods: []string{"GET", "POST", "OPTIONS"},
		AllowHeaders: []string{"Origin", "Content-Type"},
		MaxAge:       12 * time.Hour,
	}))

	router.POST("/api/trading/start", func(c *gin.Context) {
		var payload TradingCommand
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		forwardJSON(c, pythonBaseURL+"/trading/start", payload)
	})

	router.POST("/api/trading/stop", func(c *gin.Context) {
		forwardJSON(c, pythonBaseURL+"/trading/stop", gin.H{})
	})

	router.GET("/api/trading/logs", func(c *gin.Context) {
		resp, err := http.Get(pythonBaseURL + "/trading/logs")
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()
		c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
	})

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	addr := ":8080"
	log.Printf("API gateway listening on %s", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

func forwardJSON(c *gin.Context, url string, payload any) {
	body, err := json.Marshal(payload)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	resp, err := http.Post(url, "application/json", bytes.NewReader(body))
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
		return
	}
	defer resp.Body.Close()
	c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
}
