// app/layout.js
import NavBar from "../components/NavBar";
import "../styles/globals.css";

export default function Layout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>
        <NavBar />
        {children} {/* This will render the specific page content */}
      </body>
    </html>
  );
}
