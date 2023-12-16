import useSWR from "swr";
import Form, { IChangeEvent } from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { useState } from 'react';
import { json_headers } from "@/utils";


export default function Settings() {
    const fetcher = (url: string) => fetch(url).then(res => res.json());
    const {data: settings_schema, error: schema_error} = useSWR('/api/settings/openapi.json', fetcher);

    const [settings, setSettings] = useState(null);
    const [formData, setFormData] = useState(null);
    const {error: settings_error} = useSWR('/api/settings', fetcher, {onSuccess: data => {setSettings(data); setFormData(data)}});

    const handleSubmit = (e: IChangeEvent<any>) => {
        fetch('/api/settings', {
            method: 'PUT',
            headers: json_headers,
            body: JSON.stringify(e.formData),
        })
        .then(response => response.json())
        .then(data => {
            setSettings(data);
            setFormData(data);
        });
    };

    if (settings_error) return <div>Failed to load settings</div>;
    if (schema_error) return <div>Failed to load schema</div>;
    var loading: string[] = [];
    if (!settings_schema)loading = loading.concat(['Schema']);
    if (!settings)loading = loading.concat(['Settings']);
    if (loading.length > 0)
        return <div>Loading {loading.join(' and ')}...</div>;
    return (
        <Form
            schema={settings_schema}
            validator={validator}
            formData={formData}
            onChange={e => setFormData(e.formData)}
            onSubmit={handleSubmit}
        />
    );
};
