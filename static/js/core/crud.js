/**
 * Generic list/create/edit/delete renderer for the "setup/reference data"
 * resources that used to run on apps/common/crud.py's Django CRUD base
 * classes + templates/common/generic_list.html / generic_form.html /
 * generic_confirm_delete.html. Reproduces that exact markup (same Tailwind
 * classes, same structure) but built from JSON fetched via the REST API
 * instead of server-rendered template context.
 *
 * Each converted page calls one of KipsCrud.renderList/renderForm/
 * renderDeleteConfirm with a small static config object (API URLs, column
 * definitions, page URLs) - the config is page *structure*, not page
 * *data*; the actual rows/field values always come from a fetch() call.
 */
(function (global) {
    'use strict';

    const { apiFetch, ApiError } = global.KipsAPI;

    const ICONS = {
        plus: '<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />',
        warning:
            '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />',
        'check-circle':
            '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />',
    };

    function icon(name, cssClass) {
        const path = ICONS[name];
        if (!path) return '';
        return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="${cssClass}" aria-hidden="true">${path}</svg>`;
    }

    function escapeHtml(value) {
        if (value === null || value === undefined) return '';
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function getPath(obj, dottedPath) {
        return dottedPath.split('.').reduce((value, part) => (value === null || value === undefined ? '' : value[part]), obj);
    }

    function fillTemplate(template, params) {
        return template.replace(/\{(\w+)\}/g, (_, key) => encodeURIComponent(params[key]));
    }

    function renderMessageBanner(container, tag, text) {
        const classesByTag = {
            error: 'border-red-200 bg-red-50 text-red-700',
            success: 'border-green-200 bg-green-50 text-green-700',
        };
        const iconByTag = { error: 'warning', success: 'check-circle' };
        container.innerHTML = `
            <ul class="mb-6 space-y-2">
                <li class="flex items-start gap-2 rounded-lg border px-4 py-3 text-sm shadow-sm animate-fade-in-up ${classesByTag[tag] || classesByTag.error}">
                    ${icon(iconByTag[tag] || 'warning', 'h-5 w-5 shrink-0')}
                    <span>${escapeHtml(text)}</span>
                </li>
            </ul>`;
    }

    /** Reads ?msg=created|updated|deleted set by the form/delete pages after
     * a successful mutation, renders the same-styled banner the old
     * Django `messages` framework used to show, then strips it from the
     * URL so refreshing doesn't re-show it (mirrors messages being
     * consumed-once). */
    function showQueryMessage(container, successTextByKey) {
        const params = new URLSearchParams(location.search);
        const key = params.get('msg');
        if (key && successTextByKey[key]) {
            renderMessageBanner(container, 'success', successTextByKey[key]);
            params.delete('msg');
            const newSearch = params.toString();
            history.replaceState(null, '', location.pathname + (newSearch ? `?${newSearch}` : ''));
        }
    }

    // --- List page ---------------------------------------------------------

    async function renderList(config) {
        const messagesEl = document.getElementById('page-messages');
        const actionsEl = document.getElementById('crud-actions');
        const rootEl = document.getElementById('crud-list-root');

        if (messagesEl) {
            showQueryMessage(messagesEl, {
                created: config.createdMessage || 'Created.',
                updated: config.updatedMessage || 'Updated.',
                deleted: config.deletedMessage || 'Deleted.',
            });
        }

        if (actionsEl) {
            let html = '';
            (config.extraActions || []).forEach((action) => {
                html += `<a href="${escapeHtml(action.url)}" class="btn-secondary">${action.icon ? icon(action.icon, 'h-4 w-4') : ''}${escapeHtml(action.label)}</a>`;
            });
            if (config.addUrl) {
                html += `<a href="${escapeHtml(config.addUrl)}" class="btn-primary">${icon('plus', 'h-4 w-4')}Add</a>`;
            }
            actionsEl.innerHTML = html;
        }

        const params = new URLSearchParams(location.search);
        const page = params.get('page') || '1';

        let data;
        try {
            data = await apiFetch(config.apiList, { params: { page } });
        } catch (err) {
            rootEl.innerHTML = `<div class="py-8 text-center"><p class="text-sm text-red-600">Could not load data (${err.status || 'network error'}).</p></div>`;
            return;
        }

        const rows = data.results || [];
        if (rows.length === 0) {
            rootEl.innerHTML = '<div class="py-8 text-center"><p class="text-sm text-gray-500">No records yet.</p></div>';
            return;
        }

        const headerCells = config.columns.map(([, label]) => `<th>${escapeHtml(label)}</th>`).join('') + '<th></th>';
        const bodyRows = rows
            .map((row) => {
                const cells = config.columns
                    .map(([key]) => `<td>${escapeHtml(getPath(row, key))}</td>`)
                    .join('');
                let actionsCell = '';
                if (config.editUrlTemplate) {
                    actionsCell += `<a href="${escapeHtml(fillTemplate(config.editUrlTemplate, { id: row.id }))}" class="link">Edit</a>`;
                }
                if (config.deleteUrlTemplate) {
                    actionsCell += `<a href="${escapeHtml(fillTemplate(config.deleteUrlTemplate, { id: row.id }))}" class="link-danger ml-3">Delete</a>`;
                }
                return `<tr>${cells}<td class="whitespace-nowrap">${actionsCell}</td></tr>`;
            })
            .join('');

        const pageSize = config.pageSize || 50;
        const numPages = Math.max(1, Math.ceil(data.count / pageSize));
        const currentPage = parseInt(page, 10) || 1;
        let paginationHtml = '';
        if (numPages > 1) {
            const prevLink = data.previous
                ? `<a href="?page=${currentPage - 1}" class="link">&laquo; Previous</a>`
                : '<span></span>';
            const nextLink = data.next
                ? `<a href="?page=${currentPage + 1}" class="link">Next &raquo;</a>`
                : '<span></span>';
            paginationHtml = `
                <div class="mt-4 flex items-center justify-between border-t border-gray-100 pt-4 text-sm text-gray-500">
                    ${prevLink}
                    <span>Page ${currentPage} of ${numPages}</span>
                    ${nextLink}
                </div>`;
        }

        rootEl.innerHTML = `
            <div class="table-wrap">
            <table class="table-modern">
                <thead><tr>${headerCells}</tr></thead>
                <tbody>${bodyRows}</tbody>
            </table>
            </div>
            ${paginationHtml}`;
    }

    // --- Create / Edit form page --------------------------------------------

    function fieldWidgetHtml(name, meta, value) {
        const commonAttrs = `id="field_${name}" name="${name}" class="input-field"`;
        const maxlen = meta.max_length ? ` maxlength="${meta.max_length}"` : '';
        const val = value === null || value === undefined ? '' : value;

        if (meta.type === 'boolean') {
            return `<input type="checkbox" id="field_${name}" name="${name}" class="checkbox-field" ${val ? 'checked' : ''}>`;
        }
        if ((meta.type === 'related field' || meta.type === 'choice') && meta.choices) {
            const optionKey = meta.type === 'choice' ? 'value' : 'value';
            const options = meta.choices
                .map((choice) => `<option value="${escapeHtml(choice.value)}" ${String(val) === String(choice.value) ? 'selected' : ''}>${escapeHtml(choice.display_name)}</option>`)
                .join('');
            return `<select ${commonAttrs}><option value="">---------</option>${options}</select>`;
        }
        if (meta.type === 'date') {
            return `<input type="date" ${commonAttrs} value="${escapeHtml(val)}">`;
        }
        if (meta.type === 'integer' || meta.type === 'float' || meta.type === 'decimal') {
            return `<input type="number" ${commonAttrs}${maxlen} value="${escapeHtml(val)}">`;
        }
        return `<input type="text" ${commonAttrs}${maxlen} value="${escapeHtml(val)}">`;
    }

    async function renderForm(config) {
        const rootEl = document.getElementById('crud-form-root');
        const isEdit = Boolean(config.apiDetail);
        const metaUrl = isEdit ? config.apiDetail : config.apiList;

        let optionsResp;
        let existing = {};
        try {
            [optionsResp, existing] = await Promise.all([
                apiFetch(metaUrl, { method: 'OPTIONS' }),
                isEdit ? apiFetch(config.apiDetail) : Promise.resolve({}),
            ]);
        } catch (err) {
            rootEl.innerHTML = `<p class="text-sm text-red-600">Could not load this form (${err.status || 'network error'}).</p>`;
            return;
        }

        const actionKey = isEdit ? 'PUT' : 'POST';
        const fieldsMeta = optionsResp.actions[actionKey] || optionsResp.actions.POST;
        const fieldNames = Object.keys(fieldsMeta).filter((name) => name !== 'id' && !fieldsMeta[name].read_only);

        const fieldsHtml = fieldNames
            .map((name) => {
                const meta = fieldsMeta[name];
                const optionalTag = !meta.required ? '<span class="font-normal text-gray-400">(optional)</span>' : '';
                const helpText = meta.help_text ? `<p class="mt-1.5 text-xs text-gray-400">${escapeHtml(meta.help_text)}</p>` : '';
                return `
                    <div>
                        <label for="field_${name}" class="field-label">${escapeHtml(meta.label)} ${optionalTag}</label>
                        ${fieldWidgetHtml(name, meta, existing[name])}
                        ${helpText}
                        <div class="field-errors" data-field="${name}"></div>
                    </div>`;
            })
            .join('');

        rootEl.innerHTML = `
            <form id="crud-form" novalidate>
                <div id="form-non-field-errors"></div>
                <div class="space-y-4">${fieldsHtml}</div>
                <div class="mt-6 flex items-center gap-3 border-t border-gray-100 pt-5">
                    <button type="submit" class="btn-primary">Save</button>
                    <a href="${escapeHtml(config.cancelUrl)}" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-800">Cancel</a>
                </div>
            </form>`;

        document.getElementById('crud-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            document.getElementById('form-non-field-errors').innerHTML = '';
            fieldNames.forEach((name) => {
                const slot = rootEl.querySelector(`.field-errors[data-field="${name}"]`);
                if (slot) slot.innerHTML = '';
            });

            const payload = {};
            fieldNames.forEach((name) => {
                const meta = fieldsMeta[name];
                const input = document.getElementById(`field_${name}`);
                if (meta.type === 'boolean') {
                    payload[name] = input.checked;
                } else if (input.value !== '') {
                    payload[name] = input.value;
                } else if (!meta.required) {
                    payload[name] = null;
                }
            });

            try {
                if (isEdit) {
                    await apiFetch(config.apiDetail, { method: 'PATCH', body: payload });
                } else {
                    await apiFetch(config.apiList, { method: 'POST', body: payload });
                }
                const url = new URL(config.redirectUrl, location.origin);
                url.searchParams.set('msg', isEdit ? 'updated' : 'created');
                location.href = url.pathname + url.search;
            } catch (err) {
                if (err instanceof ApiError && err.status === 400 && typeof err.data === 'object') {
                    Object.entries(err.data).forEach(([key, messages]) => {
                        const text = Array.isArray(messages) ? messages.join(' ') : String(messages);
                        if (key === 'non_field_errors' || key === 'detail') {
                            document.getElementById('form-non-field-errors').innerHTML += `
                                <p class="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
                                    ${icon('warning', 'h-4 w-4 shrink-0')}${escapeHtml(text)}
                                </p>`;
                        } else {
                            const slot = rootEl.querySelector(`.field-errors[data-field="${key}"]`);
                            if (slot) slot.innerHTML = `<p class="mt-1.5 text-xs text-red-600">${escapeHtml(text)}</p>`;
                        }
                    });
                } else {
                    document.getElementById('form-non-field-errors').innerHTML = `
                        <p class="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
                            ${icon('warning', 'h-4 w-4 shrink-0')}Something went wrong. Please try again.
                        </p>`;
                }
            }
        });
    }

    // --- Delete confirm page ------------------------------------------------

    async function renderDeleteConfirm(config) {
        const titleEl = document.getElementById('crud-delete-title');
        const formEl = document.getElementById('crud-delete-form');

        let obj;
        try {
            obj = await apiFetch(config.apiDetail);
        } catch (err) {
            titleEl.textContent = 'Could not load this record.';
            return;
        }

        const title = config.titleFields.map((field) => getPath(obj, field)).join(config.titleSeparator || ' ');
        titleEl.textContent = `Delete "${title}"?`;

        formEl.addEventListener('submit', async (event) => {
            event.preventDefault();
            try {
                await apiFetch(config.apiDetail, { method: 'DELETE' });
                const url = new URL(config.redirectUrl, location.origin);
                url.searchParams.set('msg', 'deleted');
                location.href = url.pathname + url.search;
            } catch (err) {
                titleEl.insertAdjacentHTML(
                    'afterend',
                    `<p class="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
                        ${icon('warning', 'h-4 w-4 shrink-0')}Could not delete this record. It may be referenced elsewhere.
                    </p>`
                );
            }
        });
    }

    global.KipsCrud = { renderList, renderForm, renderDeleteConfirm };
})(window);
