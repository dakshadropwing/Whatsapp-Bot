import { api } from './api'

export const whatsappService = {
  getAccounts: () =>
    api.get('/whatsapp/accounts').then(r => r.data),

  sendText: (data: { phone: string; message: string }) =>
    api.post('/whatsapp/send', data).then(r => r.data),

  sendTemplate: (data: { phone: string; template_name: string; language: string; parameters: unknown[] }) =>
    api.post('/whatsapp/send-template', data).then(r => r.data),
}
