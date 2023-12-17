import Form, { IChangeEvent } from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { useState, useEffect } from 'react';
import { json_headers } from "@/utils";


export default function Settings() {
    const [settings, setSettings] = useState(null);
    const [settingsSchema, setSettingsSchema] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/api/settings/openapi.json')
            .then(r => r.json())
            .then(data => setSettingsSchema(data));

        fetch('/api/settings')
            .then(r => r.json())
            .then(data => setSettings(data))
            .catch(err => setError(err))
    }, []);

    const handleSubmit = (e: IChangeEvent<any>) => {
        fetch('/api/settings', {
            method: 'PUT',
            headers: json_headers,
            body: JSON.stringify(e.formData),
        })
        .then(response => response.json())
        .then(data => setSettings(data))
        .catch(err => setError(err));
    };

    if (error) return <div>Failed to load; error: {error}</div>;
    if (!settings || !settingsSchema)
        return <div>Loading...</div>;
    return (
        <Form
            schema={settingsSchema}
            validator={validator}
            formData={settings}
            onChange={e => setSettings(e.formData)}
            onSubmit={handleSubmit}
        />
    );
};
