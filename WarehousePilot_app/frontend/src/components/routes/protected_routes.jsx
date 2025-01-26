import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ allowedRoles }) => {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) {
        return <Navigate to="/" />;  // Redirect to login page
    }

    if (!allowedRoles.includes(user.role)) {
        // Redirect to appropriate dashboard based on role
        switch (user.role) {
            case 'admin':
                return <Navigate to="/admin_dashboard" />;
            case 'manager':
                return <Navigate to="/manager_dashboard" />;
            case 'staff':
                return <Navigate to="/staff_dashboard" />;
            case 'qa':
                return <Navigate to="/qa_dashboard" />;
            default:
                return <Navigate to="/" />;
        }  
    }
    return null;  
};

export default ProtectedRoute;
