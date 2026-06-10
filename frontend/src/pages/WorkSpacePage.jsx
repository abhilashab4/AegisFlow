import { useState } from "react";
import {
  Container,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Box,
  Divider,
  Grid,
  Stack,
  Card,
  CardContent,
  Chip
} from "@mui/material";
import {
  Security,
  AutoAwesome,
  Memory,
  AttachMoney,
  ReceiptLong,
  FactCheck
} from "@mui/icons-material";

import {
  previewSanitization,
  generateResponse
} from "../services/aiService";

export default function WorkSpacePage() {
  const [task, setTask] = useState("text-summarization");
  const [prompt, setPrompt] = useState("");
  const [preview, setPreview] = useState(null);
  const [response, setResponse] = useState(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);

  const handleReview = async () => {
    try {
      setReviewLoading(true);
      const result = await previewSanitization(prompt);
      setPreview(result);
      setResponse(null);
    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Security review failed"
      );
    } finally {
      setReviewLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerateLoading(true);
      const result = await generateResponse(prompt, task);
      setResponse(result);
    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Generation failed"
      );
    } finally {
      setGenerateLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 6 }}>
      <Grid container spacing={4}>
        
        {/* Left Column: Input Panel */}
        <Grid item xs={12} md={5}>
          <Paper
            elevation={0}
            sx={{
              p: 4,
              borderRadius: 4,
              border: "1px solid",
              borderColor: "divider",
              backgroundColor: "background.paper",
              height: "100%",
              boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.03)"
            }}
          >
            <Box sx={{ mb: 4, display: "flex", alignItems: "center", gap: 1.5 }}>
              <AutoAwesome color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: "-0.5px" }}>
                Enterprise AI Gateway
              </Typography>
            </Box>

            <Stack spacing={3}>
              <TextField
                select
                fullWidth
                label="Select Task Strategy"
                variant="outlined"
                value={task}
                onChange={(e) => setTask(e.target.value)}
              >
                <MenuItem value="text-summarization">Text Summarization</MenuItem>
                <MenuItem value="data-extraction">Data Extraction</MenuItem>
                <MenuItem value="code-generation">Code Generation</MenuItem>
                <MenuItem value="complex-reasoning">Complex Reasoning</MenuItem>
              </TextField>

              <TextField
                fullWidth
                multiline
                rows={12}
                label="Prompt Input"
                placeholder="Type or paste your analytical prompt content here..."
                variant="outlined"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    fontFamily: task === "code-generation" ? "monospace" : "inherit"
                  }
                }}
              />

              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={reviewLoading ? <CircularProgress size={20} color="inherit" /> : <Security />}
                onClick={handleReview}
                disabled={reviewLoading || !prompt.trim()}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  fontWeight: 600,
                  textTransform: "none",
                  boxShadow: "none"
                }}
              >
                {reviewLoading ? "Reviewing..." : "Review Security"}
              </Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Stack spacing={4} sx={{ height: "100%" }}>
            
            {!preview && !generateLoading && !response && (
              <Box
                sx={{
                  height: "100%",
                  minHeight: 400,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "2px dashed",
                  borderColor: "divider",
                  borderRadius: 4,
                  p: 4,
                  textAlign: "center",
                  color: "text.secondary"
                }}
              >
                <Security sx={{ fontSize: 48, mb: 2, opacity: 0.4 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Awaiting Security Audit
                </Typography>
                <Typography variant="body2" maxWidth={360}>
                  Submit your configuration input on the left to run PII scrubbing safeguards before triggering the LLM generation.
                </Typography>
              </Box>
            )}

            {preview && (
              <Paper
                elevation={0}
                sx={{
                  p: 4,
                  borderRadius: 4,
                  border: "1px solid",
                  borderColor: "success.light",
                  backgroundColor: "success.radialGradient" || "background.paper",
                  boxShadow: "0px 10px 30px rgba(46, 125, 50, 0.05)"
                }}
              >
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <FactCheck color="success" />
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      Security Verification
                    </Typography>
                  </Stack>
                  <Chip label="Passed Check" color="success" size="small" sx={{ fontWeight: 600 }} />
                </Box>

                <Alert severity="success" variant="outlined" sx={{ mb: 3, borderRadius: 2 }}>
                  Prompt successfully passed enterprise PII sanitization parameters.
                </Alert>

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, textTransform: "uppercase", fontSize: "0.75rem", letterSpacing: "0.5px", color: "text.secondary" }}>
                  Sanitized Production Payload
                </Typography>
                
                <Box
                  sx={{
                    p: 2.5,
                    borderRadius: 2,
                    backgroundColor: "action.hover",
                    border: "1px solid",
                    borderColor: "divider",
                    fontFamily: "monospace",
                    fontSize: "0.9rem",
                    whiteSpace: "pre-wrap",
                    mb: 4
                  }}
                >
                  {preview.sanitized_prompt}
                </Box>

                <Button
                  variant="contained"
                  color="success"
                  size="large"
                  fullWidth
                  startIcon={generateLoading ? <CircularProgress size={20} color="inherit" /> : <AutoAwesome />}
                  onClick={handleGenerate}
                  disabled={generateLoading}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    textTransform: "none"
                  }}
                >
                  {generateLoading ? "Generating..." : "Approve & Execute Generation"}
                </Button>
              </Paper>
            )}

            {generateLoading && (
              <Paper
                elevation={0}
                sx={{
                  p: 6,
                  borderRadius: 4,
                  border: "1px solid",
                  borderColor: "divider",
                  textAlign: "center",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center"
                }}
              >
                <CircularProgress size={40} thickness={4} sx={{ mb: 3 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Querying Distributed Architecture
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Compiling your request payload safely across infrastructure nodes...
                </Typography>
              </Paper>
            )}

            {response && (
              <Paper
                elevation={0}
                sx={{
                  p: 4,
                  borderRadius: 4,
                  border: "1px solid",
                  borderColor: "primary.main",
                  boxShadow: "0px 12px 40px rgba(25, 118, 210, 0.06)"
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
                  Inference Output Response
                </Typography>

                <Box
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    backgroundColor: "action.hover",
                    border: "1px solid",
                    borderColor: "divider",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                    fontSize: "1rem",
                    mb: 4
                  }}
                >
                  {response.response}
                </Box>

                <Divider sx={{ mb: 3 }} />

                {/* Metrics Meta Metadata Grid */}
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, textTransform: "uppercase", fontSize: "0.75rem", color: "text.secondary" }}>
                  Execution Analytics
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Card variant="outlined" sx={{ borderRadius: 2 }}>
                      <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ color: "text.secondary", mb: 0.5 }}>
                          <Memory fontSize="small" />
                          <Typography variant="caption" fontWeight={600}>Model & Core Architecture</Typography>
                        </Stack>
                        <Typography variant="body2" fontWeight={700}>
                          {response.model} <Box component="span" sx={{ fontWeight: 400, color: "text.secondary" }}>via {response.provider}</Box>
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined" sx={{ borderRadius: 2 }}>
                      <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ color: "text.secondary", mb: 0.5 }}>
                          <ReceiptLong fontSize="small" />
                          <Typography variant="caption" fontWeight={600}>Total Tokens</Typography>
                        </Stack>
                        <Typography variant="body1" fontWeight={700}>
                          {Number(response.prompt_tokens) + Number(response.completion_tokens)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {response.prompt_tokens} in / {response.completion_tokens} out
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "success.light", bgcolor: "success.light" && "transparent" }}>
                      <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ color: "success.main", mb: 0.5 }}>
                          <AttachMoney fontSize="small" />
                          <Typography variant="caption" fontWeight={700}>Computed Cost</Typography>
                        </Stack>
                        <Typography variant="body1" fontWeight={700} color="success.main">
                          ${response.estimated_cost}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          USD Valuation
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Paper>
            )}

          </Stack>
        </Grid>

      </Grid>
    </Container>
  );
}