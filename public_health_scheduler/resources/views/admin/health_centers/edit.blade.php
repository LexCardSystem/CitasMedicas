<x-admin-layout>
    <h2>Edit Health Center: {{ $healthCenter->name ?? '' }}</h2>
    <form method="POST" action="{{ route('admin.health-centers.update', $healthCenter->id ?? 0) }}">
        @csrf
        @method('PUT')
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" value="{{ old('name', $healthCenter->name ?? '') }}" required>
        </div>
        <div>
            <label for="address">Address:</label>
            <input type="text" id="address" name="address" value="{{ old('address', $healthCenter->address ?? '') }}" required>
        </div>
        <div>
            <label for="contact_info">Contact Info:</label>
            <input type="text" id="contact_info" name="contact_info" value="{{ old('contact_info', $healthCenter->contact_info ?? '') }}">
        </div>
<div><label for="operating_hours_json">Operating Hours (JSON):</label><textarea name="operating_hours_json" id="operating_hours_json" rows="5">{{ old('operating_hours_json', isset($healthCenter) && $healthCenter->operating_hours ? json_encode($healthCenter->operating_hours, JSON_PRETTY_PRINT) : '') }}</textarea><small>Example: { "monday": {"open": "08:00", "close": "17:00"} }</small></div>
<div class='mt-4'><h4>Assign Staff (Doctors)</h4><select name="staff_ids[]" multiple size="5">@foreach($staffUsers ?? [] as $staff)<option value="{{ $staff->id }}" {{ (isset($healthCenter) && $healthCenter->staff->contains($staff->id)) ? 'selected' : '' }}>{{ $staff->name }}</option>@endforeach</select></div>
        <button type="submit">Update Health Center</button>
    </form>
</x-admin-layout>
