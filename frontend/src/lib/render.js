export function renderSublocationName(sublocation) {
  return `${sublocation.name} (${sublocation.location_data.name})`;
}

export function renderLocationName(location) {
  return `${location.name} (${location.location_owner_data.email})`;
}

export function renderTicketCategory(ticketCategory) {
  return `${ticketCategory.name} (${ticketCategory.event_data.name})`;
}
