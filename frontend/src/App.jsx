import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import WorkspacePage from "./pages/WorkspacePage";

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<LoginPage />}
        />

        <Route
          path="/workspace"
          element={<WorkspacePage />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;