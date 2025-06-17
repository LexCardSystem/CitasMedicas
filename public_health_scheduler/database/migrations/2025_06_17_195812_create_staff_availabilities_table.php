<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('staff_availabilities', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade'); // Staff/Doctor User ID
            $table->foreignId('health_center_id')->constrained()->onDelete('cascade');
            $table->tinyInteger('day_of_week'); // 0 for Sunday, 1 for Monday, ..., 6 for Saturday
            $table->time('start_time');
            $table->time('end_time');
            $table->date('effective_date_start')->nullable(); // For specific date ranges
            $table->date('effective_date_end')->nullable();   // For specific date ranges
            $table->boolean('is_available')->default(true); // To mark specific slots as unavailable (e.g. breaks)
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('staff_availabilities');
    }
};
