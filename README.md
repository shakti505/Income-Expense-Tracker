# Enhanced Budgeting Application Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Core Features](#core-features)
4. [API Documentation](#api-documentation)
5. [Technical Implementation](#technical-implementation)
6. [Database Schema](#database-schema)

## System Overview

The Enhanced Budgeting Application is a comprehensive financial management system that helps users track expenses, manage budgets, and achieve savings goals. The system implements advanced features including recurring transactions, notifications, and detailed analytics.

### Key Features
- Advanced user authentication with role-based access
- Budget management with notifications
- Recurring transactions
- Detailed financial reports and analytics
- Savings plan tracking
- Data export capabilities

## Authentication & Authorization

### User Roles

#### Regular User
- Access to personal financial data
- Manage personal budgets and transactions
- View personal analytics and reports
- Create and track savings goals

#### Admin User
- All regular user capabilities
- Manage user accounts
- View aggregated system data
- Access admin dashboard

### Authentication Flow

```python
from rest_framework_simplejwt.tokens import RefreshToken

class UserAuthentication:
    def login(self, username, password):
        """
        Authenticate user and generate JWT tokens
        
        Returns:
            dict: Contains access_token and refresh_token
        """
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
        raise AuthenticationFailed("Invalid credentials")
```

## Core Features

### Budget Management

#### Budget Model
```python
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Notification thresholds
    WARNING_THRESHOLD = 90  # Percentage
    CRITICAL_THRESHOLD = 100  # Percentage
```

#### Budget Notification System
```python
@shared_task
def check_budget_thresholds():
    """
    Celery task to check budget thresholds and send notifications
    """
    budgets = Budget.objects.filter(active=True)
    for budget in budgets:
        percentage_used = calculate_budget_usage(budget)
        if percentage_used >= Budget.CRITICAL_THRESHOLD:
            send_critical_notification(budget)
        elif percentage_used >= Budget.WARNING_THRESHOLD:
            send_warning_notification(budget)
```

### Recurring Transactions

#### Transaction Scheduler
```python
class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_due_date = models.DateField()
```

#### Cron Job Implementation
```python
@shared_task
def process_recurring_transactions():
    """
    Daily cron job to process recurring transactions
    """
    today = timezone.now().date()
    due_transactions = RecurringTransaction.objects.filter(
        next_due_date=today,
        active=True
    )
    
    for transaction in due_transactions:
        create_transaction(transaction)
        update_next_due_date(transaction)
```

### Savings Plans

#### Savings Plan Model
```python
class SavingsPlan(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ]
    
    FREQUENCY_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        return (self.current_amount / self.target_amount) * 100
    
    @property
    def required_contribution(self):
        """Calculate required periodic contribution"""
        remaining_amount = self.target_amount - self.current_amount
        remaining_periods = self.calculate_remaining_periods()
        return remaining_amount / remaining_periods if remaining_periods > 0 else 0
```

## API Documentation

### Budget Management APIs

```python
# GET /api/v1/budgets/
class BudgetListView(APIView):
    """
    List all budgets for the authenticated user
    """
    def get(self, request):
        budgets = Budget.objects.filter(user=request.user)
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)

# POST /api/v1/budgets/
    def post(self, request):
        """Create a new budget"""
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

### Savings Plan APIs

```python
# GET /api/v1/savings-plans/{id}/
class SavingsPlanDetailView(APIView):
    """
    Retrieve detailed information about a savings plan
    """
    def get(self, request, plan_id):
        plan = get_object_or_404(SavingsPlan, id=plan_id, user=request.user)
        serializer = SavingsPlanSerializer(plan)
        return Response({
            **serializer.data,
            'progress_percentage': plan.progress_percentage,
            'required_contribution': plan.required_contribution,
            'time_remaining': plan.calculate_remaining_time()
        })
```

## Technical Implementation

### Notification System

```python
class NotificationService:
    @staticmethod
    def send_budget_alert(user, budget, percentage_used):
        """
        Send budget alert notification
        """
        subject = f"Budget Alert: {budget.category.name}"
        message = (
            f"You have used {percentage_used}% of your "
            f"{budget.category.name} budget for {budget.month}/{budget.year}"
        )
        send_email_notification.delay(user.email, subject, message)
```

### Report Generation

```python
class ReportGenerator:
    @staticmethod
    def generate_spending_report(user, start_date, end_date):
        """
        Generate detailed spending report
        """
        transactions = Transaction.objects.filter(
            user=user,
            date__range=(start_date, end_date)
        )
        
        report_data = {
            'total_spending': transactions.aggregate(Sum('amount')),
            'category_breakdown': transactions.values('category__name')
                .annotate(total=Sum('amount')),
            'daily_spending': transactions.values('date')
                .annotate(total=Sum('amount'))
        }
        
        return report_data
```

## Database Schema

### Core Tables

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Budgets Table
CREATE TABLE budgets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(10,2) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category_id, year, month)
);

-- Savings Plans Table
CREATE TABLE savings_plans (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) DEFAULT 0,
    deadline DATE NOT NULL,
    priority VARCHAR(10) NOT NULL,
    frequency VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Security Considerations

1. Authentication
   - JWT tokens with short expiration times
   - Refresh token rotation
   - Rate limiting on authentication endpoints

2. Authorization
   - Role-based access control
   - Object-level permissions
   - API endpoint protection

3. Data Protection
   - Encrypted sensitive data
   - Regular backups
   - Audit logging for sensitive operations

