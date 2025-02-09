//import your routes here

import { dashboard_routes } from './dashboard_routes';
import { authentication_routes } from './authentication_routes';
import { order_routes } from './order_routes';
import { label_routes } from './label_routes';

const routes = [...authentication_routes, ...dashboard_routes, ...label_routes, ...order_routes];
export default routes;