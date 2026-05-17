import React from 'react';

const SettingsField = ({ label, description, children }) => {
  return (
    <div className="settings-field">
      <div className="settings-field-info">
        <label className="settings-field-label">{label}</label>
        {description && <p className="settings-field-description">{description}</p>}
      </div>
      <div className="settings-field-control">
        {children}
      </div>
    </div>
  );
};

export default SettingsField;
