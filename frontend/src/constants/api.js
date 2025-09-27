// Configuration API et constantes
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000',
  API_VERSION: 'v1',
  TIMEOUT: 30000,
};

// Endpoints API
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login/',
    REGISTER: '/api/v1/auth/register/',
    REFRESH: '/api/v1/auth/refresh/',
    LOGOUT: '/api/v1/auth/logout/',
  },
  
  // Core
  CORE: {
    ADDRESSES: '/api/v1/core/addresses/',
    CONTACTS: '/api/v1/core/contacts/',
    ACTIVITY_LOGS: '/api/v1/core/activity-logs/',
  },
  
  // Members
  MEMBERS: {
    MEMBERS: '/api/v1/members/members/',
    MEMBERSHIP_FEES: '/api/v1/members/membership-fees/',
  },
  
  // Inventory
  INVENTORY: {
    CATEGORIES: '/api/v1/inventory/categories/',
    UNITS: '/api/v1/inventory/units/',
    PRODUCTS: '/api/v1/inventory/products/',
    STOCK_MOVEMENTS: '/api/v1/inventory/stock-movements/',
    INVENTORIES: '/api/v1/inventory/inventories/',
  },
  
  // Sales
  SALES: {
    CUSTOMERS: '/api/v1/sales/customers/',
    SALES: '/api/v1/sales/sales/',
  },
  
  // Finance
  FINANCE: {
    ACCOUNTS: '/api/v1/finance/accounts/',
    TRANSACTIONS: '/api/v1/finance/transactions/',
    MEMBER_SAVINGS: '/api/v1/finance/member-savings/',
    LOANS: '/api/v1/finance/loans/',
    LOAN_PAYMENTS: '/api/v1/finance/loan-payments/',
    BUDGETS: '/api/v1/finance/budgets/',
    BUDGET_LINES: '/api/v1/finance/budget-lines/',
  },
  
  // Reports
  REPORTS: {
    REPORTS: '/api/v1/reports/reports/',
    DASHBOARDS: '/api/v1/reports/dashboards/',
    REPORT_TEMPLATES: '/api/v1/reports/report-templates/',
  },
};

// Status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// Local storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  THEME_MODE: 'theme_mode',
  LANGUAGE: 'language',
};