<x-admin-layout>
    <h2>Add New Health Center</h2>
    <form method="POST" action="{{ route('admin.health-centers.store') }}">
        @csrf
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" value="{{ old('name') }}" required>
        </div>
        <div>
            <label for="address">Address:</label>
            <input type="text" id="address" name="address" value="{{ old('address') }}" required>
        </div>
        <div>
            <label for="contact_info">Contact Info:</label>
            <input type="text" id="contact_info" name="contact_info" value="{{ old('contact_info') }}">
        </div>
<div><label for="operating_hours_json">Operating Hours (JSON):</label><textarea name="operating_hours_json" id="operating_hours_json" rows="5">{{ old('operating_hours_json', isset($healthCenter) && $healthCenter->operating_hours ? json_encode($healthCenter->operating_hours, JSON_PRETTY_PRINT) : '') }}</textarea><small>Example: { "monday": {"open": "08:00", "close": "17:00"} }</small></div>
        <button type="submit">Save Health Center</button>
    </form>
</x-admin-layout>
