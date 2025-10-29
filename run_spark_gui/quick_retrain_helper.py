"""
Quick Retrain Helper - For parameter tuning without reloading data
"""
import subprocess
import os
from pathlib import Path


class QuickRetrainHelper:
    """Helper class for quick model retraining with new parameters"""
    
    PRESETS = {
        'default': {
            'name': 'Default (Baseline)',
            'rank': 50,
            'alpha': 40.0,
            'regParam': 0.1,
            'maxIter': 20,
            'expected_map': '5.5-6.0%',
            'time': '15-18 min'
        },
        'moderate': {
            'name': 'Moderate Performance',
            'rank': 60,
            'alpha': 45.0,
            'regParam': 0.08,
            'maxIter': 25,
            'expected_map': '6.0-6.5%',
            'time': '18-22 min'
        },
        'aggressive': {
            'name': 'High Performance',
            'rank': 80,
            'alpha': 50.0,
            'regParam': 0.05,
            'maxIter': 30,
            'expected_map': '7.0-7.5%',
            'time': '22-27 min'
        },
        'maximum': {
            'name': 'Maximum Performance',
            'rank': 100,
            'alpha': 60.0,
            'regParam': 0.03,
            'maxIter': 35,
            'expected_map': '8.0-8.5%',
            'time': '27-35 min'
        }
    }
    
    @staticmethod
    def delete_old_model(log_callback=None):
        """Delete old model from HDFS"""
        try:
            if log_callback:
                log_callback("🗑️  Deleting old model...", "info")
            
            result = subprocess.run(
                ["docker", "exec", "namenode", "hdfs", "dfs", "-rm", "-r", "/output/model/als_model"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if log_callback:
                if result.returncode == 0:
                    log_callback("✅ Model deleted successfully", "success")
                else:
                    log_callback("ℹ️  No old model found (OK)", "info")
            
            return True
        except Exception as e:
            if log_callback:
                log_callback(f"⚠️  Error deleting model: {e}", "warning")
            return False
    
    @staticmethod
    def clear_progress_tracker(log_callback=None):
        """Clear progress tracker from containers"""
        try:
            if log_callback:
                log_callback("🗑️  Clearing progress tracker...", "info")
            
            for worker in ["gui-docker-spark-worker-1", "gui-docker-spark-worker-2"]:
                subprocess.run(
                    ["docker", "exec", worker, "rm", "-f", "/tmp/progress.json"],
                    capture_output=True,
                    timeout=10
                )
            
            if log_callback:
                log_callback("✅ Progress cleared", "success")
            
            return True
        except Exception as e:
            if log_callback:
                log_callback(f"⚠️  Error clearing progress: {e}", "warning")
            return False
    
    @staticmethod
    def copy_code_to_container(filepath, container, log_callback=None):
        """Copy Python code to container"""
        try:
            if log_callback:
                log_callback(f"📦 Copying code to {container}...", "info")
            
            result = subprocess.run(
                ["docker", "cp", filepath, f"{container}:/tmp/"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if log_callback:
                    log_callback("✅ Code copied successfully", "success")
                return True
            else:
                if log_callback:
                    log_callback(f"❌ Failed to copy code: {result.stderr}", "error")
                return False
                
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error copying code: {e}", "error")
            return False
    
    @staticmethod
    def submit_retrain_job(container, master, filename, params, log_callback=None, timeout=None):
        """Submit retrain job with custom parameters"""
        try:
            if log_callback:
                log_callback("🚀 Submitting retrain job...", "info")
                log_callback(f"   Rank: {params['rank']}", "info")
                log_callback(f"   Alpha: {params['alpha']}", "info")
                log_callback(f"   RegParam: {params['regParam']}", "info")
                log_callback(f"   MaxIter: {params['maxIter']}", "info")
            
            # Build command (no -it flag for Popen compatibility)
            cmd = [
                "docker", "exec", container,
                "/spark/bin/spark-submit",
                "--master", master,
                f"/tmp/{filename}",
                "--rank", str(params['rank']),
                "--alpha", str(params['alpha']),
                "--regParam", str(params['regParam']),
                "--maxIter", str(params['maxIter'])
            ]
            
            # Use subprocess.Popen for streaming output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='replace',  # Replace invalid chars instead of crashing
                bufsize=1
            )
            
            # Stream output
            if log_callback:
                for line in process.stdout:
                    log_callback(line.rstrip(), "log")
            
            process.wait(timeout=timeout)
            
            if process.returncode == 0:
                if log_callback:
                    log_callback("✅ Training completed successfully!", "success")
                return True
            else:
                if log_callback:
                    log_callback(f"❌ Training failed with code {process.returncode}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback("⏱️  Training timeout - job may still be running", "warning")
            return False
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error submitting job: {e}", "error")
            return False
    
    @staticmethod
    def quick_retrain(filepath, container, master, preset_name='default', custom_params=None, log_callback=None):
        """
        Quick retrain workflow:
        1. Delete old model
        2. Clear progress
        3. Copy code
        4. Submit with new params
        """
        
        # Get parameters
        if custom_params:
            params = custom_params
            if log_callback:
                log_callback("🎯 Using custom parameters", "header")
        else:
            params = QuickRetrainHelper.PRESETS.get(preset_name, QuickRetrainHelper.PRESETS['default'])
            if log_callback:
                log_callback(f"🎯 Using preset: {params['name']}", "header")
                log_callback(f"   Expected MAP: {params['expected_map']}", "info")
                log_callback(f"   Estimated time: {params['time']}", "info")
        
        # Step 1: Delete model
        if not QuickRetrainHelper.delete_old_model(log_callback):
            return False
        
        # Step 2: Clear progress
        if not QuickRetrainHelper.clear_progress_tracker(log_callback):
            return False
        
        # Step 3: Copy code
        filename = Path(filepath).name
        if not QuickRetrainHelper.copy_code_to_container(filepath, container, log_callback):
            return False
        
        # Step 4: Submit job
        return QuickRetrainHelper.submit_retrain_job(
            container, master, filename, params, log_callback, timeout=7200  # 2 hours
        )

