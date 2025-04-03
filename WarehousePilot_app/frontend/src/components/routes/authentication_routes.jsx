import { Login } from '../authentication';
import ForgotPassword from '../authentication/ForgotPassword';

export const authentication_routes = [
  { path: '/', element: <Login /> },
  { path: '/forgot-password', element: <ForgotPassword /> },
];