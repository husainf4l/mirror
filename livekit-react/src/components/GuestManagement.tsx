import React, { useState, useEffect } from 'react';
import './GuestManagement.css';

interface Guest {
  id?: number;
  first_name: string;
  last_name: string;
  full_name?: string;
  phone?: string;
  seat_number?: string;
  relation?: string;
  relation_type?: string;
  relation_type_id?: number;
  message?: string;
  story?: string;
  about?: string;
  created_at?: string;
  updated_at?: string;
}

interface RelationType {
  id: number;
  name: string;
  description: string;
}

const GuestManagement: React.FC = () => {
  const [guests, setGuests] = useState<Guest[]>([]);
  const [relationTypes, setRelationTypes] = useState<RelationType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingGuest, setEditingGuest] = useState<Guest | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const [formData, setFormData] = useState<Guest>({
    first_name: '',
    last_name: '',
    phone: '',
    seat_number: '',
    relation: '',
    relation_type_id: undefined,
    message: '',
    story: '',
    about: ''
  });

  useEffect(() => {
    fetchGuests();
    fetchRelationTypes();
  }, []);

  const fetchGuests = async () => {
    try {
      const response = await fetch('/api/guests', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setGuests(data.guests);
      } else {
        showMessage('Failed to fetch guests', 'error');
      }
    } catch (error) {
      showMessage('Error fetching guests', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchRelationTypes = async () => {
    try {
      const response = await fetch('/api/relation-types', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setRelationTypes(data.relation_types);
      }
    } catch (error) {
      console.error('Error fetching relation types:', error);
    }
  };

  const showMessage = (text: string, type: 'success' | 'error') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : value
    }));
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      phone: '',
      seat_number: '',
      relation: '',
      relation_type_id: undefined,
      message: '',
      story: '',
      about: ''
    });
    setEditingGuest(null);
    setShowAddForm(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingGuest ? `/api/guests/${editingGuest.id}` : '/api/guests';
      const method = editingGuest ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage(
          editingGuest ? 'Guest updated successfully' : 'Guest created successfully',
          'success'
        );
        await fetchGuests();
        resetForm();
      } else {
        showMessage(data.message || 'Operation failed', 'error');
      }
    } catch (error) {
      showMessage('Error saving guest', 'error');
    }
  };

  const handleEdit = (guest: Guest) => {
    setFormData({
      first_name: guest.first_name,
      last_name: guest.last_name,
      phone: guest.phone || '',
      seat_number: guest.seat_number || '',
      relation: guest.relation || '',
      relation_type_id: guest.relation_type_id,
      message: guest.message || '',
      story: guest.story || '',
      about: guest.about || ''
    });
    setEditingGuest(guest);
    setShowAddForm(true);
  };

  const handleDelete = async (guestId: number, guestName: string) => {
    if (!window.confirm(`Are you sure you want to delete ${guestName}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/guests/${guestId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage('Guest deleted successfully', 'success');
        await fetchGuests();
      } else {
        showMessage(data.message || 'Delete failed', 'error');
      }
    } catch (error) {
      showMessage('Error deleting guest', 'error');
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await fetch('/api/guests/export', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `wedding_guests_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showMessage('Excel file downloaded successfully', 'success');
      } else {
        showMessage('Failed to export guests', 'error');
      }
    } catch (error) {
      showMessage('Error exporting guests', 'error');
    }
  };

  const handleImportExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const fileContent = event.target?.result as string;
        
        const response = await fetch('/api/guests/import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            file_content: fileContent
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          showMessage(`Successfully imported ${data.imported_count} guests`, 'success');
          await fetchGuests();
        } else {
          showMessage(data.message || 'Import failed', 'error');
        }
      };
      reader.readAsDataURL(file);
    } catch (error) {
      showMessage('Error importing guests', 'error');
    }
    
    // Reset file input
    e.target.value = '';
  };

  const filteredGuests = guests.filter(guest =>
    guest.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    guest.phone?.includes(searchTerm) ||
    guest.relation?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    guest.seat_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="guest-management">
        <div className="loading">Loading guests...</div>
      </div>
    );
  }

  return (
    <div className="guest-management">
      <div className="header">
        <h2>Guest Management</h2>
        <div className="header-actions">
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn btn-primary"
          >
            {showAddForm ? 'Cancel' : 'Add Guest'}
          </button>
          <button 
            onClick={handleExportExcel}
            className="btn btn-secondary"
          >
            Export Excel
          </button>
          <label className="btn btn-secondary file-upload">
            Import Excel
            <input 
              type="file" 
              accept=".xlsx,.xls"
              onChange={handleImportExcel}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {showAddForm && (
        <div className="add-form">
          <h3>{editingGuest ? 'Edit Guest' : 'Add New Guest'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label>First Name *</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Last Name *</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="form-group">
                <label>Seat Number</label>
                <input
                  type="text"
                  name="seat_number"
                  value={formData.seat_number}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="form-group">
                <label>Relation</label>
                <input
                  type="text"
                  name="relation"
                  value={formData.relation}
                  onChange={handleInputChange}
                />
              </div>
              
              <div className="form-group">
                <label>Relation Type</label>
                <select
                  name="relation_type_id"
                  value={formData.relation_type_id || ''}
                  onChange={handleInputChange}
                >
                  <option value="">Select relation type</option>
                  {relationTypes.map(rt => (
                    <option key={rt.id} value={rt.id}>{rt.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label>Message</label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                rows={3}
              />
            </div>
            
            <div className="form-group">
              <label>Story</label>
              <textarea
                name="story"
                value={formData.story}
                onChange={handleInputChange}
                rows={3}
              />
            </div>
            
            <div className="form-group">
              <label>About</label>
              <textarea
                name="about"
                value={formData.about}
                onChange={handleInputChange}
                rows={3}
              />
            </div>
            
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                {editingGuest ? 'Update Guest' : 'Create Guest'}
              </button>
              <button type="button" onClick={resetForm} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="search-section">
        <input
          type="text"
          placeholder="Search guests by name, phone, relation, or seat..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <span className="guest-count">
          Showing {filteredGuests.length} of {guests.length} guests
        </span>
      </div>

      <div className="guests-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Seat</th>
              <th>Relation</th>
              <th>Type</th>
              <th>Message</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredGuests.map(guest => (
              <tr key={guest.id}>
                <td>
                  <div className="guest-name">
                    <strong>{guest.full_name}</strong>
                  </div>
                </td>
                <td>{guest.phone || '-'}</td>
                <td>{guest.seat_number || '-'}</td>
                <td>{guest.relation || '-'}</td>
                <td>{guest.relation_type || '-'}</td>
                <td>
                  <div className="message-preview">
                    {guest.message ? (
                      guest.message.length > 50 
                        ? `${guest.message.substring(0, 50)}...`
                        : guest.message
                    ) : '-'}
                  </div>
                </td>
                <td>
                  <div className="actions">
                    <button
                      onClick={() => handleEdit(guest)}
                      className="btn btn-small btn-edit"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(guest.id!, guest.full_name!)}
                      className="btn btn-small btn-delete"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredGuests.length === 0 && (
          <div className="no-guests">
            {searchTerm ? 'No guests match your search.' : 'No guests added yet.'}
          </div>
        )}
      </div>
    </div>
  );
};

export default GuestManagement;