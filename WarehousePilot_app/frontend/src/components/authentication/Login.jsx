import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './authentication.css';


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [shake, setShake] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const rememberedUsername = localStorage.getItem('rememberedUsername');
    if (rememberedUsername) {
      setUsername(rememberedUsername);
      setRememberMe(true);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login/`, { username, password });
      const { access, user } = response.data;


      localStorage.setItem('token', access);
      localStorage.setItem('user', JSON.stringify(user));
      if (rememberMe) {
        localStorage.setItem('rememberedUsername', username);
      } else {
        localStorage.removeItem('rememberedUsername');
      }
      if (user.role === 'admin') {
        navigate('/admin_dashboard');
      } else if (user.role === 'manager') {
        navigate('/manager_dashboard');
      } else if (user.role === 'staff') {
        navigate('/manager_dashboard');
      } else if (user.role === 'qa') {
        navigate('/manager_dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setError('Login failed. Please try again.');
      setShake(true);
      setTimeout(() => setShake(false), 500);
    }
  };
  return (
    <div className="min-h-screen flex flex-col md:flex-row dark:bg-gray-900">
      {/* Login Form - Centered on mobile */}
      <div className="w-full md:w-1/2 p-8 flex flex-col justify-center mx-auto max-w-2xl">
        <div className="w-full space-y-8">
          <div className="text-center">
            <img
              src="csf-logo-footer-edited.png"
              alt="Company Logo"
              className="h-16 mx-auto mb-8"
            />
            <h1 className="text-3xl font-bold mb-8 dark:text-white">Sign In</h1>
          </div>

          <form onSubmit={handleLogin} className={`space-y-8 ${shake ? 'animate-shake' : ''}`}>
            <div>
              <label className="block text-lg font-medium mb-3 dark:text-gray-300">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter Username"
                className="w-full px-4 py-3 border rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-400"
              />
            </div>

            <div>
              <label className="block text-lg font-medium mb-3 dark:text-gray-300">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter password"
                className="w-full px-4 py-3 border rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-400"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center dark:text-gray-300">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-5 w-5 text-blue-600 dark:text-blue-500"
                />
                <span className="ml-2 text-lg">Remember me</span>
              </label>
              <a
                href="#"
                onClick={(e) => {
                  navigate('/forgot-password');
                }}
                className="text-lg text-gray-500 hover:underline dark:text-gray-400"
              >
                Forgot Password
              </a>
            </div>

            <button
              type="submit"
              className="w-full py-3 px-4 bg-black text-white rounded-lg transition-colors duration-200 text-lg font-medium hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
            >
              Sign In
            </button>

            {error && (
              <p className="text-red-600 dark:text-red-400 text-lg text-center" data-testid="login-error">
                {error}
              </p>
            )}
          </form>
        </div>
      </div>

      {/* Right side - Image (hidden below 1000px) */}
      <div className="hidden md:block w-1/2 bg-gray-100 dark:bg-gray-800 hide-below-1000">
        <img
          src="sign-in-img1.png"
          alt="Worker with laptop"
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  );
}

export default Login;