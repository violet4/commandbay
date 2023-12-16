import useSWR from "swr";
import Form, { IChangeEvent } from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { FormEvent } from 'react';
import { json_headers } from "@/utils";


export default function Settings() {
    const fetcher = (url: string) => fetch(url).then(res => res.json());
    const {data: settings_schema, error: schema_error} = useSWR('/api/settings/openapi.json', fetcher);
    const {data: settings, error: settings_error} = useSWR('/api/settings', fetcher);
    // Cannot find name 'ISubmitEvent'. Did you mean 'SubmitEvent'?ts(2552)
    // lib.dom.d.ts(21821, 13): 'SubmitEvent' is declared here.
    // type ISubmitEvent = /*unresolved*/ any
    const handleSubmit = (e: IChangeEvent<any>) => {
        // Your custom submit logic goes here
        const formData = e.formData;
        console.log("Form data submitted:", formData);

        // For example, sending data to your API:
        fetch('/api/settings', {
            method: 'PUT',
            headers: json_headers,
            body: JSON.stringify(formData),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
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
            formData={settings}
            onSubmit={handleSubmit}
        />
    );
};
