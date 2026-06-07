import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Button,
  Container,
  Paper,
  TextField,
  Typography
} from "@mui/material";

import { login } from "../services/authService";

export default function LoginPage() {

  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {

    try {

      const data = await login(
        username,
        password
      );

      localStorage.setItem(
        "token",
        data.access_token
      );

      navigate("/workspace");

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Login failed"
      );
    }
  };

  return (

    <Container
      maxWidth="sm"
      sx={{ mt: 10 }}
    >

      <Paper
        elevation={4}
        sx={{ p: 4 }}
      >

        <Typography
          variant="h4"
          gutterBottom
        >
          Enterprise AI Gateway
        </Typography>

        <TextField
          fullWidth
          label="Username"
          margin="normal"
          value={username}
          onChange={(e) =>
            setUsername(e.target.value)
          }
        />

        <TextField
          fullWidth
          label="Password"
          type="password"
          margin="normal"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <Button
          variant="contained"
          fullWidth
          sx={{ mt: 2 }}
          onClick={handleLogin}
        >
          Login
        </Button>

      </Paper>

    </Container>
  );
}