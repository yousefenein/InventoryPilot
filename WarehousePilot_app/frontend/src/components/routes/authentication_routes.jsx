import { Login } from '../authentication';
import ForgotPassword from '../authentication/ForgotPassword';
import ResetPassword from '../authentication/ResetPassword';

export const authentication_routes = [
  { path: '/', element: <Login /> },
  { path: '/forgot-password', element: <ForgotPassword /> },
  { path: '/reset-password/:uid/:token', element: <ResetPassword /> },
];