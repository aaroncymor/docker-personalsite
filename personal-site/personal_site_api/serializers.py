from django.contrib.auth.models import User

from rest_framework import serializers

from blog.models import Category, Post, Tag, Decipher


class UserSerializer(serializers.HyperlinkedModelSerializer):
    _link = serializers.HyperlinkedIdentityField(
        view_name='api:user-detail'
    )
    class Meta:
        model = User
        fields = ('_link', 'username', 'first_name', 'last_name', 
                  'email', 'groups', 'user_permissions', 'is_staff',
                  'is_superuser', 'last_login', 'date_joined'
                )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    _link = serializers.HyperlinkedIdentityField(
        view_name='api:category-detail'
    )
    #posts = serializers.HyperlinkedRelatedField(
    #   many=True,
    #   view_name='api:post-detail',
    #   read_only=True
    #)
    class Meta:
        model = Category
        fields = ('_link', 'id', 'name', 'timestamp')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    _link = serializers.HyperlinkedIdentityField(
        view_name='api:post-detail'
    )

    category = CategorySerializer()
    content = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()

    # Create another serializer for Post that has different fields.
    class DecipherSimpleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Decipher
            fields = ('id', 'name', 'challenge',
                    'clue', 'code')
    #tags = serializers.HyperlinkedRelatedField(
    #    many=True,
    #    view_name='api:tag-detail',
    #    read_only=True
    #)
    
    deciphers = DecipherSimpleSerializer(many=True)

    class Meta:
        model = Post
        fields = ('_link', 'id', 'category', 'title', 'short_content', 'content', 'deciphers', 'published_date', 'timestamp')

    def get_content(self, obj):
        if not obj.content:
            return None
        
        return obj.sanitized_content
    
    def get_short_content(self, obj):
        if not obj.content:
            return None
        
        return obj.short_content_for_list
    

class TagSerializer(serializers.HyperlinkedModelSerializer):
    _link = serializers.HyperlinkedIdentityField(
        view_name='api:tag-detail'
    )
    post = PostSerializer()

    class Meta:
        model = Tag
        fields = ('_link', 'id', 'tag', 'post', 'timestamp')


class DecipherSerializer(serializers.HyperlinkedModelSerializer):
    _link = serializers.HyperlinkedIdentityField(
        view_name='api:decipher-detail'
    )
    post = PostSerializer()
    class Meta:
        model = Decipher
        fields = ('_link', 'id', 'post', 'name', 
        'challenge', 'clue', 'code')


# Autocomplete

class PostSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content')