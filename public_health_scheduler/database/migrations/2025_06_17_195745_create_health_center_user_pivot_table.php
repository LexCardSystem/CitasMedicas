<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('health_center_user', function (Blueprint $table) {
            $table->id();
            $table->foreignId('health_center_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade'); // Staff/Doctor User ID
            $table->timestamps();
            $table->unique(['health_center_id', 'user_id']); // Prevent duplicates
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('health_center_user');
    }
};
