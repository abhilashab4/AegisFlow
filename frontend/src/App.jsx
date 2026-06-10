import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import WorkSpacePage from "./pages/WorkSpacePage";

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
          element={<WorkSpacePage />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;