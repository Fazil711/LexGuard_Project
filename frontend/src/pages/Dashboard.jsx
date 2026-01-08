import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // New Case Form State
  const [showModal, setShowModal] = useState(false);
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseCategory, setNewCaseCategory] = useState('General');

  // 1. Fetch Cases on Load
  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      const res = await api.get('/cases/'); // Trailing slash might matter depending on router
      setCases(res.data);
    } catch (err) {
      console.error("Failed to fetch cases", err);
    } finally {
      setLoading(false);
    }
  };

  // 2. Handle Create Case
  const handleCreateCase = async (e) => {
    e.preventDefault();
    try {
      await api.post('/cases/', {
        title: newCaseTitle,
        category: newCaseCategory
      });
      setShowModal(false);
      setNewCaseTitle('');
      fetchCases(); // Refresh list
    } catch (err) {
      alert("Failed to create case");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-lex-600 rounded-lg flex items-center justify-center text-white font-bold">L</div>
          <span className="text-xl font-bold text-lex-900">LexGuard</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-600">Hello, {user?.name}</span>
          <button onClick={logout} className="text-sm text-red-500 hover:text-red-700 font-medium">
            Sign Out
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Legal Cases</h1>
          <button 
            onClick={() => setShowModal(true)}
            className="bg-lex-600 hover:bg-lex-700 text-white px-5 py-2.5 rounded-lg font-medium shadow-sm transition-colors"
          >
            + New Case
          </button>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="text-gray-500">Loading your cases...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.length === 0 && (
              <div className="col-span-full text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500 text-lg">No cases found. Create one to get started.</p>
              </div>
            )}
            
            {cases.map((c) => (
              <div 
                key={c.id} 
                onClick={() => navigate(`/cases/${c.id}`)}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full 
                    ${c.status === 'closed' ? 'bg-gray-100 text-gray-600' : 'bg-green-100 text-green-700'}`}>
                    {c.status.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-lex-600 transition-colors">
                  {c.title}
                </h3>
                <p className="text-sm text-gray-500">Category: {c.category}</p>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Simple Modal for New Case */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Create New Case</h2>
            <form onSubmit={handleCreateCase}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Case Title</label>
                <input 
                  type="text" 
                  required
                  className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-lex-500 outline-none"
                  placeholder="e.g. Vendor Agreement Dispute"
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select 
                  className="w-full p-2 border rounded-lg bg-white"
                  value={newCaseCategory}
                  onChange={(e) => setNewCaseCategory(e.target.value)}
                >
                  <option value="General">General</option>
                  <option value="Contract">Contract Dispute</option>
                  <option value="Employment">Employment Issue</option>
                  <option value="Compliance">Compliance</option>
                </select>
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 bg-lex-600 text-white rounded-lg hover:bg-lex-700"
                >
                  Create Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}