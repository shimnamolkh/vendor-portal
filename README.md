# Vendor Portal - LLM-Driven Entry Management System

A modern, premium web application for vendor document submission and management, built with React and Vite.

## 🚀 Features

### Authentication & Session Management
- Secure vendor login system
- Persistent display of vendor's legal name (Vendor Session Entity) across all forms
- Session-based tracking of all vendor activities

### Dual-Workflow Interface

#### 1. **Supplier Inward Entries** (Mandatory Documentation)
- **Required Documents:**
  - Invoice (Primary Reference Document)
  - Delivery Order (DO)
  - Purchase Order (LPO)
- **Submission Gating:** Submit button is disabled until all three mandatory documents are uploaded
- Optional remarks field for additional notes
- Real-time validation and file preview

#### 2. **Direct Purchase Entries** (Optional Documentation)
- Flexible document upload (0 or more files)
- Supports multiple file formats: PDF, JPG, PNG, DOC, DOCX
- Drag-and-drop file upload interface
- Can submit without any documents attached

#### 3. **Submission History**
- View all past entries (both Supplier Inward and Direct Purchase)
- Filter by entry type
- Status tracking (APPROVED, PENDING, REJECTED)
- Detailed entry information including:
  - Entry ID and type
  - Submission timestamp
  - Attached documents
  - Remarks
  - Current status

## 🎨 Design Features

- **Premium Dark Theme** with vibrant gradients
- **Glassmorphism** effects for modern UI
- **Smooth Animations** and micro-interactions
- **Responsive Design** for all screen sizes
- **Custom Scrollbars** with gradient styling
- **Loading States** and success animations

## 📋 Technical Stack

- **Frontend Framework:** React 18
- **Build Tool:** Vite 6
- **Styling:** Vanilla CSS with CSS Variables
- **Typography:** Google Fonts (Inter)
- **Icons:** Custom SVG icons

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd vENDORPORTAL
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
vENDORPORTAL/
├── src/
│   ├── components/
│   │   ├── LoginPage.jsx          # Authentication interface
│   │   ├── LoginPage.css
│   │   ├── VendorDashboard.jsx    # Main dashboard with tabs
│   │   ├── VendorDashboard.css
│   │   ├── SupplierInwardEntry.jsx    # Tab A: Mandatory docs
│   │   ├── SupplierInwardEntry.css
│   │   ├── DirectPurchaseEntry.jsx    # Tab B: Optional docs
│   │   ├── DirectPurchaseEntry.css
│   │   ├── SubmissionHistory.jsx      # View past entries
│   │   └── SubmissionHistory.css
│   ├── App.jsx                    # Main app component
│   ├── App.css
│   ├── main.jsx                   # React entry point
│   └── index.css                  # Global styles & design system
├── index.html
├── vite.config.js
├── package.json
└── VENDOR_PORTAL_SPECIFICATION.md  # Detailed requirements doc
```

## 🔐 Mock Authentication

For development purposes, the application uses mock authentication:
- **Username:** Any text
- **Password:** Any text
- **Mock Vendor:** Acme Corporation Global Ltd.

In production, replace the mock authentication in `LoginPage.jsx` with actual API calls.

## 📡 API Integration

The application is designed to integrate with the following API endpoints (currently mocked):

### Authentication
- `POST /api/v1/auth/login` - Vendor login
- `GET /api/v1/auth/session` - Get session info

### Submissions
- `POST /api/v1/entries/inward` - Submit supplier inward entry
- `POST /api/v1/entries/direct` - Submit direct purchase entry
- `GET /api/v1/entries/history` - Get vendor's submission history

## 🎯 Key Requirements Met

✅ Vendor authentication with legal name capture  
✅ Persistent "Vendor Session Entity" display  
✅ Two distinct entry workflows (Supplier Inward & Direct Purchase)  
✅ Mandatory document validation for Supplier Inward  
✅ Optional document upload for Direct Purchase  
✅ Submission gating based on document upload status  
✅ Submission history with filtering  
✅ Premium, modern UI design  
✅ Responsive layout  
✅ Smooth animations and transitions  

## 🔄 Future Enhancements

- Real backend API integration
- Document preview functionality
- Advanced search and filtering in history
- Export submission history to PDF/Excel
- Email notifications for status changes
- Multi-language support
- Dark/Light theme toggle

## 📄 License

This project is proprietary software developed for vendor management purposes.

## 👥 Support

For technical support or questions, please contact the development team.

---

**Built with ❤️ using React + Vite**
