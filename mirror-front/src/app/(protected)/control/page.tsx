'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function ControlPage() {
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Mirror Control Panel</h1>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Link
              href="/mirror"
              className="bg-blue-600 hover:bg-blue-700 text-white p-6 rounded-lg shadow-md transition-colors text-center block"
            >
              <div className="text-2xl font-bold mb-2">Mirror</div>
              <div className="text-blue-100">Access the interactive wedding mirror</div>
            </Link>
            
            <Link
              href="/admin"
              className="bg-green-600 hover:bg-green-700 text-white p-6 rounded-lg shadow-md transition-colors text-center block"
            >
              <div className="text-2xl font-bold mb-2">Admin</div>
              <div className="text-green-100">System administration and settings</div>
            </Link>
            
            <div className="bg-gray-400 text-white p-6 rounded-lg shadow-md text-center">
              <div className="text-2xl font-bold mb-2">Guests</div>
              <div className="text-gray-200">Guest management (Coming Soon)</div>
            </div>
          </div>
          
          <div className="mt-8 bg-gray-50 p-6 rounded-lg">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-gray-700">LiveKit Connection: Ready</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-gray-700">Mirror System: Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}